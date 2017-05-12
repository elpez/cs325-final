import nltk

from nltk.tree import Tree

from spanishdictionary import spanishDictionary

class LexicalTransfer:

	def __init__(self):
		self.needs_subject = True

	def transfer(self, sent):
		sentence = ""
		for child in sent:
			if not isinstance(child, Tree): #if it's a tuple of (word, tag)
				word = child[0].lower()
				if child[1] == 'n' or child[1] == 'p':
					self.needs_subject = False
				if child[1] == 'v':
					sentence += self.transfer_verb(word) + ' '
					self.needs_subject = True
				elif child[1] == 'U': #tries all methods
					transverb = self.transfer_verb(word)
					if word != transverb:
						sentence += transverb + ' '
					else:
						if word in spanishDictionary:
							sentence += spanishDictionary[word][0] + ' ' #uses the first word that is a synonym
						else:
							sentence += child[0] + ' '
				else:
					if word != "" and word in spanishDictionary:
						sentence += spanishDictionary[word][0] + ' ' #uses the first word that is a synonym
					else:
						sentence += child[0] + ' '
			else:
				sentence += self.transfer(child)
		return sentence

	def transfer_verb(self, verb):
		english_verb = verb #not English yet, but it will be eventually
		verbs = open('jehle_verb_database.csv','r').readlines() #database from https://github.com/ghidinelli/fred-jehle-spanish-verbs
		for line in verbs:
			if verb in line:
				init_conjugations = line.split('","')
				conjugations = []
				for word in init_conjugations:
					conjugations += [word.strip('\n').strip('\r').strip('"')]
				english_verb = conjugations[6].split(' ')[1].strip(',')
				if verb == conjugations[0]: #infinitive
					return 'to ' + english_verb
				elif verb == conjugations[7] and self.needs_subject: #1s
					return 'I ' + english_verb 
				elif verb == conjugations[8] and self.needs_subject: #2s
					return 'you ' + english_verb
				elif verb == conjugations[9] and self.needs_subject: #3s
					return 'they ' + english_verb
				elif verb == conjugations[10] and self.needs_subject: #1p
					return 'we ' + english_verb
				elif verb == conjugations[11] and self.needs_subject: #2p
					return 'you ' + english_verb
				elif verb == conjugations[12] and self.needs_subject: #3p
					return 'they ' + english_verb
				elif verb == conjugations[13]: #gerund
					return conjugations[14]
				elif verb == conjugations[15]: #past participle
					return conjugations[16]
		return english_verb
