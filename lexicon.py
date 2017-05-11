import nltk

from nltk.tree import Tree

from spanishdictionary import spanishDictionary

def lexical_transfer(tree):
	sentence = ""
	for child in tree:
		if not isinstance(child, Tree): #if it's a string
			sentence += spanishDictionary[child][0] + " " #uses the first word that is a synonym
		else:
			sentence += lexical_transfer(child)
	return sentence
