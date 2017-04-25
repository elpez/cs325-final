from operator import itemgetter

from tbl import *
from cfg import CFGrammar, tree_to_str

sent = 'el hombre ve la mujer'

def parse(tags):
    grammar = CFGrammar.from_file('grammar.txt')
    return grammar.parse(tags, key=itemgetter(1))
