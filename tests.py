#!/usr/bin/env python3
import unittest

import tbl

class SimpleTagger(tbl.Tagger):
    tagset = ('JJ', 'DET', 'NN', 'TO', 'VB')

class TaggerTests(unittest.TestCase):
    def test_small(self):
        # the point of this corpus is to generate a NN -> VB / TO _ rule
        corpus = [('the', 'DET'), ('horse', 'NN'), ('wants', 'VB'), ('to', 'TO'), ('race', 'VB'),
                  ('the', 'DET'), ('race', 'NN'), ('happened', 'VB'),
                  ('the', 'DET'), ('race', 'NN'), ('continued', 'VB')]
        tagger = SimpleTagger(corpus)
        self.assertEqual(tagger.most_likely_tag('race'), 'NN')
        self.assertEqual(tagger.most_likely_tag('the'), 'DET')
        self.assertEqual(len(tagger.transforms), 1)
        self.assertEqual(tagger.transforms[0], tbl.Transform('NN', 'VB', 'TO'))
        self.assertEqual(tagger.tag('the race'), [('the', 'DET'), ('race', 'NN')])
        self.assertEqual(tagger.tag('to race'), [('to', 'TO'), ('race', 'VB')])
        self.assertEqual(tagger.tag('the horse continued the race'),
                         [('the', 'DET'), ('horse', 'NN'), ('continued', 'VB'), ('the', 'DET'),
                          ('race', 'NN')])

if __name__ == '__main__':
    unittest.main()
