#!/usr/bin/env python3
import unittest

import tbl

class SimpleTagger(tbl.Tagger):
    tagset = ('JJ', 'DET', 'NN', 'TO', 'VB')

class BrownTagger(tbl.Tagger):
    tagset = ('.', '(', ')', '*', '--', ',', ':', 'ABL', 'ABN', 'ABX', 'AP',
              'AT', 'BE', 'BED', 'BEDZ', 'BEG', 'BEM', 'BEN', 'BER', 'BEZ', 'CC', 'CD',
              'CS', 'DO', 'DOD', 'DOZ', 'DT', 'DTI', 'DTX', 'EX', 'FW', 'HV', 'HVD',
              'HVG', 'HVN', 'IN', 'JJ', 'JJR', 'JJS', 'JJT', 'MD', 'NC', 'NN', 'NN$',
              'NNS', 'NNS$', 'NP', 'NP$', 'NPS', 'NPS$', 'NR', 'OD', 'PN', 'PN$', 'PP$',
              'PP$$', 'PPL', 'PPLS', 'PPO', 'PPS', 'PPSS', 'PRP', 'PRP$', 'QL', 'QLP',
              'RB', 'RBR', 'RBT', 'RN', 'RP', 'TO', 'UH', 'VB', 'VBD', 'VBG', 'VBN',
              'VBP', 'VBZ', 'WDT', 'WPO', 'WPS', 'WQL', 'WRB')

class TaggerTests(unittest.TestCase):
    def test_small(self):
        # the point of this corpus is to generate a NN -> VB / TO _ rule
        corpus = [('the', 'DET'), ('horse', 'NN'), ('wants', 'VB'), ('to', 'TO'), ('race', 'VB'),
                  ('the', 'DET'), ('race', 'NN'), ('happened', 'VB'),
                  ('the', 'DET'), ('race', 'NN'), ('continued', 'VB')]
        tagger = SimpleTagger(corpus)
        self.assertEqual(tagger.tag_word('race'), 'NN')
        self.assertEqual(tagger.tag_word('the'), 'DET')
        self.assertEqual(len(tagger.transforms), 1)
        self.assertEqual(tagger.transforms[0], tbl.Transform('NN', 'VB', 'TO'))
        self.assertEqual(tagger.tag('the race'), [('the', 'DET'), ('race', 'NN')])
        self.assertEqual(tagger.tag('to race'), [('to', 'TO'), ('race', 'VB')])
        self.assertEqual(tagger.tag('the horse continued the race'),
                         [('the', 'DET'), ('horse', 'NN'), ('continued', 'VB'), ('the', 'DET'),
                          ('race', 'NN')])

if __name__ == '__main__':
    unittest.main()
