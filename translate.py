"""
>>> translate('Yo tengo un perro')
['I have a dog']
"""
from tbl import cess_tagger
from lexicon import LexicalTransfer
from syntax import syntactic_transfer
from cfg import CFGrammar, Tree

def translate(sentence):
    #tagger = Tagger.load('cess.tag')
    g = CFGrammar.from_file('grammar.txt')
    tags = cess_tagger.tag(sentence)
    trees = g.parse(tags)
    lexical_transfer = LexicalTransfer()
    if trees:
        transferred = [syntactic_transfer(tree) for tree in trees]
        return [lexical_transfer.transfer(tree) for tree in transferred]
    else:
        transferred = syntactic_transfer(tags)
        return [lexical_transfer.transfer(transferred)]

print translate('Yo tengo un perro rojo')
print translate('Tienes un perro amarillo')
print translate('Ella ama el perro grande')
