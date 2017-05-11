"""
>>> translate('Yo tengo un perro')
['I have a dog']
"""
from tbl import Tagger
from lexicon import lexical_transfer
from syntax import syntactic_transfer
from cfg import CFGrammar
from operator import itemgetter

def translate(sentence):
    tagger = Tagger.load('cess.tag')
    g = CFGrammar.from_file('grammar.txt')
    tags = tagger.tag(sentence)
    trees = g.parse(tags,key=itemgetter(1))
    return [tree_to_sentence(lexical_transfer(syntactic_transfer(tree))) for tree in trees]

print str(translate('Yo tener un perro'))
