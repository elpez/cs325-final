def make_dictionary():
	dictFile = open('spanishdictionaryunformatted.txt','r')
	dictStrings = dictFile.readlines() #list of the lines, which contains the dictionary entries as strings
	dictFile.close()
	spanishDict = {}
	for dictLine in dictStrings: #iterates through dictionary entries to convert them into an actual dict
		dictLine = dictLine.replace('\n', '')
		entryList = dictLine.split('\t') #list of [English versions, Spanish versions, simplified pos]
		englishWords = entryList[0].split(';') #list of English words
		spanishWords = entryList[1].split(';') #list of Spanish words
		for englishWord in englishWords:
			englishWord = englishWord.lstrip()
		for spanishWord in spanishWords:
			spanishWord = spanishWord.lstrip()
			spanishDict[spanishWord] = englishWords #puts all the English words as possible definitions for the Spanish words
	dictFile = open('spanishdictionary.py','w')
	dictFile.write('spanishDictionary = ' + str(spanishDict))
	dictFile.close()
	return spanishDict

make_dictionary()
