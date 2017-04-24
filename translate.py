"""
>>> translate('Yo tengo un perro')
'I have a dog'
"""
from tbl import Tagger

def translate(sentence):
    tagger = Tagger.load('espanol.tag')
    g = CFGrammar.from_file('grammar.txt')
    tags = tagger.tag(sentence)
    tree = g.parse(tags)
    tree = syntactic_transfer(tree)
    tree = lexical_transfer(tree)
    return tree_to_sentence(tree)
