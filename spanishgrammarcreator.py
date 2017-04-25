import nltk

from nltk.corpus import cess_esp

from nltk.tree import Tree

def MakeSpanishGrammar(filelist):
	grammar = []
	for fileid in filelist: 
		for tree in cess_esp.parsed_sents(fileid): #for each sentence in the corpus
			rules = getStructure(tree)
			for newRule in rules: #gets the grammar rules used in that sentence and adds them to the grammar
				if newRule not in grammar: #makes sure it doesn't double-count
					grammar += newRule
	target = open('spanishgrammar.py','w')
	target.write('spanishGrammar = ' + str(grammar))
	target.close()
	return grammar

def getStructure(tree): #makes a list of all the rules used in the sentence
	if not isinstance(tree,Tree):
		return []
	rules = []
	currentRule = [tree.label() + " ->"] #each rule is a list of a key-string and a value-list, to be put into the grammar eventually
	for child in tree:
		if isinstance(child, Tree):
			currentRule[0] += " " + child.label() #adds the child to the value-list
			newRules = getStructure(child) #checks each of the children for the rules they contain
			rules += newRules
		else:
			currentRule[0] += " " + child
	rules += [currentRule]
	return rules

def checkGrammar(grammar): #mostly for debugging
	for key in grammar:
		print(key)

print(MakeSpanishGrammar(cess_esp.fileids()) #the grammar is very long. be careful.
