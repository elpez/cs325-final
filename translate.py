"""
>>> translate('Yo tengo un perro')
['I have a dog']
"""
from tbl import Tagger
from lexicon import lexical_transfer
from syntax import syntactic_transfer
from cfg import CFGrammar, Tree

def translate(sentence):
    tagger = Tagger.load('cess.tag')
    g = CFGrammar.from_file('grammar.txt')
    tags = tagger.tag(sentence)
    #print "Tags: " + str(tags)
    trees = g.parse(tags)
    if trees:
        #print 'Tree: ' + str(trees)
        transferred = [syntactic_transfer(tree) for tree in trees]
        #print 'Transferred: ' + str(transferred)
        return [lexical_transfer(tree) for tree in transferred]
    else:
        return [lexical_transfer(Tree('-', tags))]

print str(translate('Yo tener un perro rojo .'))
