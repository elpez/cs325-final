"""Context-free grammars in Python.

Initialize a grammar from a string
>>> g = CFGrammar('EXPR -> EXPR OP EXPR | NUMBER')

Create and access rules using indexing and slicing
>>> g['NUMBER'] = '/[0-9]+(\.[0-9]+)?/'
>>> g['OP'] = '+ | -'
>>> g['EXPR']
['EXPR', 'OP', 'EXPR']
>>> g['OP':]
(['+'], ['-'])
>>> g[:'NUMBER']
('EXPR',)

Length, containment, __str__, and smallstr
>>> len(g)
5
>>> 'EXPR' in g
True
>>> 'RABBIT' in g
False
>>> print(g)
EXPR -> EXPR OP EXPR
EXPR -> NUMBER
NUMBER -> /[0-9]+(\.[0-9]+)?/
OP -> +
OP -> -
>>> print(g.smallstr())
EXPR -> EXPR OP EXPR | NUMBER
NUMBER -> /[0-9]+(\.[0-9]+)?/
OP -> + | -

Renaming rules and generating a set of all symbols used in the grammar
>>> g.rename('NUMBER', 'NUM')
>>> print(g.smallstr())
EXPR -> EXPR OP EXPR | NUM
NUM -> /[0-9]+(\.[0-9]+)?/
OP -> + | -
>>> g.syms() == {'EXPR', 'NUM', 'OP', '+', '-'}
True

Recognition and parsing (including ambiguous parses)
>>> g.recognize('1237 - 23.4')
True
>>> trees = g.parse('4 - 4.5 + 2.3')
>>> len(trees)
2
>>> print trees[0]
(EXPR
  (EXPR (EXPR (NUM 4)) (OP -) (EXPR (NUM 4.5)))
  (OP +)
  (EXPR (NUM 2.3)))
>>> print trees[1]
(EXPR
  (EXPR (NUM 4))
  (OP -)
  (EXPR (EXPR (NUM 4.5)) (OP +) (EXPR (NUM 2.3))))

Parsing with tokens
>>> g2 = CFGrammar('S -> Det N V Adv')
>>> sent = [('the', 'Det'), ('woman', 'N'), ('runs', 'V'), ('quickly', 'Adv')]
>>> trees = g2.parse(sent, key=itemgetter(1))
>>> len(trees)
1
>>> print trees[0] # nltk handles the part-of-speech tag formatting
(S the/Det woman/N runs/V quickly/Adv)
"""
import re
import random
from itertools import combinations_with_replacement, count, product
from copy import copy
from operator import itemgetter

from nltk.tree import Tree

def default_tokenizer(s):
    return s.split() if isinstance(s, str) else list(s)

class CFGrammar(object):
    """A class to represent context-free grammars."""
    # these are meta-tokens to parse the right hand sides of rules
    tokens = (
        ('REGEX', r'(/[^/]*/)'),
        ('QUOTE', r'"[^"]+"'),
        ('WORD', r'[^\s|]+'),
        ('PIPE', r'\|'),
        ('MISMATCH', r'.'),
    )

    def __init__(self, iterable=None, tokenizer=default_tokenizer):
        """Initialize the grammar, optionally providing an iterable. If given, the iterable should 
           yield successive context-free rules as strings.  If the iterable is a string, then 
           splitlines will be called on it.  When processing the iterable, blank lines and lines 
           that begin with a pound mark are ignored.
        """
        self.pattern = re.compile('|'.join('(?P<%s>%s)' % p for p in self.tokens))
        self.tokenizer = tokenizer
        if isinstance(iterable, str):
            iterable = iterable.splitlines()
        self.rules = []
        if iterable is not None:
            for line in iterable:
                line = line.strip()
                if line and not line.startswith('#'):
                    try:
                        lhs, _, rhs = line.split(None, 2)
                        self[lhs] = rhs
                    except ValueError:
                        pass
        if self.rules:
            self.start = self.rules[0].left
        else:
            self.start = None

    @classmethod
    def from_file(cls, fpath):
        with open(fpath, 'r') as fsock:
            obj = cls(fsock)
        return obj

    def extend(self, other):
        """Add all the rules in the CFGrammar other to self."""
        for rule in other:
            self[rule.left] = rule.right

    def __getitem__(self, key):
        """Return the right hand sides of all rules whose left hand side matches the key.

              grammar['S']  -> first rule whose lhs is 'S'
              grammar['S:'] -> a tuple of all rules whose lhs is 'S'
              grammar[:'NP VP'] -> a tuple of all rules whose rhs is 'NP VP'
        """
        if isinstance(key, slice):
            if key.start is not None and key.stop is None:
                return self.get_rhs(key.start)
            elif key.stop is not None and key.start is None:
                return self.get_lhs(key.stop)
            else:
                raise ValueError('either start or stop of slice must be specified, but not both')
        elif isinstance(key, str):
            all_matches = self.get_rhs(key)
            if all_matches:
                return all_matches[0]
            else:
                raise IndexError
        else:
            return self.rules[key]

    def get_rhs(self, key):
        """Given the left hand side of a rule, return a tuple of all matching right hand sides."""
        return tuple(rule.right for rule in self.rules if rule.left == key)

    def get_lhs(self, key):
        """Given the right hand side of a rule, return a tuple of all matching left hand sides. If 
           key is a string, it is split before matching occurs; otherwise it is coerced into a list.
        """
        key = self.tokenizer(key)
        all_lhs = tuple(rule.left for rule in self.rules if rule.matches(key))
        return tuple(set(all_lhs))

    def __setitem__(self, lhs, rhs):
        """Add a new rule to the grammar. lhs is a string; rhs is any sequence. If rhs is a string, 
           it will be split. Note that this function does not overwrite old rules with the same left
           hand side.
        """
        for variation in self._parse_rhs(rhs):
            if variation:
                # set the start symbol, if the rules are empty
                if len(self.rules) == 0:
                    self.start = lhs
                self.rules.append(CFRule(lhs, variation, self.tokenizer))
            else:
                raise ValueError('right hand side of rule cannot be empty')

    def __delitem__(self, key):
        if isinstance(key, slice):
            if key.start is None and key.stop is None:
                del self.rules[:]
            else:
                if key.stop is not None:
                    tokenized = self.tokenizer(key.stop)
                else:
                    tokenized = None
                i = 0
                while i < len(self.rules):
                    lhs, rhs = self.rules[i].left, self.rules[i].right
                    if (key.start is None or lhs == key.start) and \
                       (key.stop is None or rhs == tokenized):
                        del self.rules[i]
                    else:
                        i += 1
        else:
            raise NotImplementedError

    def _parse_rhs(self, rhs):
        if isinstance(rhs, str):
            current = []
            for mo in self.pattern.finditer(rhs):
                kind = mo.lastgroup
                value = mo.group(kind)
                if kind == 'PIPE':
                    yield current
                    current = []
                elif kind == 'QUOTE':
                    current.append(value[1:-1])
                elif kind != 'MISMATCH':
                    current.append(value)
            if current:
                yield current
        else:
            yield list(rhs)

    def syms(self):
        """Return a set of all symbols (terminals and nonterminals) appearing in the grammar."""
        ret = set()
        for rule in self.rules:
            ret.add(rule.left)
            for sym in rule.right:
                if not sym.startswith('/') or not sym.endswith('/'):
                    ret.add(sym)
        return ret

    def rename(self, old, new):
        """Rename a rule, changing all occurrences of its name."""
        for rule in self.rules:
            if rule.left == old:
                rule.left = new
            for i, sym in enumerate(rule):
                if sym == old:
                    rule[i] = new

    def minimize(self):
        """Remove any rule whose left hand side does not ever appear on the right hand side of 
           another rule.
        """
        unmarked = self.syms()
        # the start symbol is marked by default
        if self.start:
            unmarked.remove(self.start)
        # mark all symbols that appear on the right hand side of a rule
        for rule in self.rules:
            for sym in rule:
                if sym in unmarked:
                    unmarked.remove(sym)
        # remove all rules whose left hand side was left unmarked self.rules = [rule for rule in self.rules if rule.left not in unmarked]

    def recognize(self, sent, symbol=None):
        """Return True if the sentence could be generated by the grammar from the given symbol. If 
           symbol is not specified, it defaults to the start symbol. The sentence should be a 
           sequence of tokens.
        """
        return len(self.parse(sent, symbol)) > 0

    def parse(self, sent, symbol=None, key=None):
        """Return a list of all possible parse trees for the given sentence. For details on the 
           parameters, see the CFGrammar.recognize method. A parse tree is a tuple of the form 
           (LABEL, CHILD0, CHILD1, ...).
        """
        return earley_parse(self, sent, symbol, key=key)

    def __contains__(self, item):
        return any(rule.left == item for rule in self.rules)

    def __iter__(self):
        return iter(self.rules)

    def __len__(self):
        return len(self.rules)

    def __repr__(self):
        return 'CFGrammar({})'.format(repr(self.smallstr()))

    def __str__(self):
        return '\n'.join(map(str, self.rules))

    def smallstr(self):
        """Return the grammar as a minimal string. Rules with multiple definitions are collapsed 
           into a single rule.
        """
        ret = []
        already_used = []
        for rule in self.rules:
            if rule.left in already_used:
                continue
            all_rhs = self[rule.left:]
            all_rhs_str = ' | '.join(map(' '.join, all_rhs))
            ret.append('{} -> {}'.format(rule.left, all_rhs_str))
            already_used.append(rule.left)
        return '\n'.join(ret)

    def random_derivation(self, start=None):
        """Return a random derivation from this grammar."""
        if start is None:
            start = self.start
        try:
            rule = random.choice(self[start:])
        except ValueError:
            return ''
        else:
            deriv = []
            for sym in rule:
                if sym in self:
                    deriv.append(self.random_derivation(start=sym))
                else:
                    deriv.append(sym)
            return ' '.join(deriv)

class CFRule(object):
    """A class to represent context-free rules."""

    def __init__(self, left, right, tokenizer=default_tokenizer):
        self.left = left
        self.right = right
        self.tokenizer = default_tokenizer
        self.regexes = []
        for sym in self.right:
            if sym.startswith('/') and sym.endswith('/') and len(sym) >= 2:
                pattern = '^' + sym[1:-1] + '$'
                self.regexes.append(re.compile(pattern))
            else:
                self.regexes.append(None)

    def matches(self, token, index=-1):
        """Return True if the given token matches the rule at the index. If the index is not 
           specified or is given as -1, then it attempts to match the entire right hand side of the 
           rule.
        """
        if index != -1:
            if self.regexes[index] is not None:
                return self.regexes[index].match(token)
            else:
                return self.right[index] == token
        else:
            all_tokens = self.tokenizer(token)
            for i, subtoken in enumerate(all_tokens):
                if not self.matches(subtoken, i):
                    return False
            return True

    def insert(self, key, item):
        self.right.insert(key, item)

    def pop(self, key):
        return self.right.pop(key)

    def __getitem__(self, key):
        return self.right[key]

    def __setitem__(self, key, val):
        self.right[key] = val

    def __delitem__(self, key):
        del self.right[key]

    def __contains__(self, key):
        return key in self.right

    def __len__(self):
        return len(self.right)

    def __iter__(self):
        return iter(self.right)

    def __eq__(self, other):
        return self.left == other.left and self.right == other.right

    def __repr__(self):
        return 'CFRule({0.left}, {0.right})'.format(self)

    def __str__(self):
        return '{} -> {}'.format(self.left, ' '.join(self.right))

def unique(excluding, suggestion=''):
    """Return a string that is not already in the excluding container. If suggestion is given, then 
       the new name will be based on it. In the unlikely event that a unique string cannot be found,
       a ValueError is raised.
    """
    if suggestion:
        if suggestion not in excluding:
            return suggestion
        # append numbers to the suggestion to make it unique
        for i in count(0):
            new_suggestion = suggestion + str(i)
            if new_suggestion not in excluding:
                return new_suggestion
    # generate some combination of the first seven letters of the alphabet
    for name in combinations_with_replacement('ABCDEFG', 3):
        name = ''.join(name)
        if name not in excluding:
            return name
    raise ValueError('could not find unique name')


### EARLEY PARSING

def earley_parse(grammar, sent, symbol=None, key=None):
    """Parse the sentence using the Earley algorithm. For details on parameters and return values, 
       see the CFGrammar.parse method.
    """
    if symbol is None:
        symbol = grammar.start
    words = default_tokenizer(sent)
    chart = [[] for i in range(len(words) + 1)]
    # add dummy start state
    chart[0].append(EarleyState(CFRule('y', [symbol]), 0, 0))
    for i in range(len(words) + 1):
        for state in chart[i]:
            if not state.finished():
                if state.next() in grammar:
                    earley_predict(chart, i, state, grammar)
                elif i < len(words):
                    earley_scan(chart, i, state, words, key)
            else:
                earley_complete(chart, i, state)
    ret = []
    for state in chart[-1]:
        if state.rule.left == symbol and state.origin == 0 and \
           state.finished():
            ret.append(state.to_tree())
    return ret

def earley_recognize(grammar, words, symbol=None):
    """Recognize the sentence using the Earley algorithm. For details on parameters and return 
       values, see the CFGrammar.recognize method.
    """
    return len(earley_parse(grammar, words, symbol)) > 0

def earley_predict(chart, i, state, grammar):
    symbol = state.next()
    for rule in grammar:
        if rule.left == symbol:
            s = EarleyState(rule, 0, i)
            if s not in chart[i]:
                chart[i].append(s)

def earley_scan(chart, i, state, words, key):
    symbol = state.next()
    this_word = key(words[i]) if key is not None else words[i]
    if state.rule.matches(this_word, state.progress):
        s = state.make_progress(words[i])
        if s not in chart[i+1]:
            chart[i+1].append(s)

def earley_complete(chart, i, state):
    for other in chart[state.origin]:
        if not other.finished() and other.next() == state.rule.left:
            s = other.make_progress(state)
            if s not in chart[i]:
                chart[i].append(s)

class EarleyState(object):
    """A state used by the Earley algorithm."""

    def __init__(self, rule, progress, origin, constituents=None):
        self.rule = rule
        self.progress = progress
        self.origin = origin
        self.constituents = constituents if constituents is not None else []

    def make_progress(self, constituent):
        new_constituents = self.constituents + [constituent]
        return EarleyState(self.rule, self.progress + 1, self.origin, new_constituents)

    def finished(self):
        return self.progress == len(self.rule)

    def next(self):
        return self.rule[self.progress]

    def to_tree(self):
        children = []
        for c in self.constituents:
            if isinstance(c, EarleyState):
                children.append(c.to_tree())
            else:
                children.append(c)
        return Tree(self.rule.left, children)

    def __eq__(self, other):
        return self.rule == other.rule and self.progress == other.progress \
           and self.origin == other.origin and self.constituents == other.constituents

    def __str__(self):
        with_dot = self.rule[:self.progress] + ['.'] + self.rule[self.progress:]
        rule_str = self.rule.left + ' -> ' + ' '.join(with_dot)
        return '({}, {})'.format(rule_str, self.origin)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
