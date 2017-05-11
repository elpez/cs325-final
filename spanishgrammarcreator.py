import nltk
from collections import Counter

from nltk.corpus import cess_esp

from nltk.tree import Tree

from tbl import normalize_tag

def MakeSpanishGrammar(filelist):
	grammar = Counter()
	for fileid in filelist: 
		for tree in cess_esp.parsed_sents(fileid): #for each sentence in the corpus
                        grammar += getStructure(tree)
	target = open('spanishgrammar.py','w')
	#target.write('spanishGrammar = ' + str(grammar))
        target.write('\n'.join(k for k, v in grammar.items() if v > 1))
	target.close()
	return grammar

def getStructure(tree): #makes a list of all the rules used in the sentence
	if not isinstance(tree,Tree):
		return Counter()
	rules = Counter()
	currentRule = normalize_tag(tree.label()) + " ->" #each rule is a list of a key-string and a value-list, to be put into the grammar
	for child in tree:
		if isinstance(child, Tree):
			currentRule += " " + normalize_tag(child.label()) #adds the child to the value-list
			rules += getStructure(child)
	rules.update([currentRule])
	return rules

def checkGrammar(grammar): #mostly for debugging
	for key in grammar:
		print(key)

MakeSpanishGrammar(cess_esp.fileids()) #the grammar is very long. be careful.

#['t5-9.tbf', u't6-0.tbf', u't6-1.tbf', u't6-2.tbf', u't6-3.tbf', u't6-4.tbf', u't6-5.tbf', u't6-6.tbf'] for testing
