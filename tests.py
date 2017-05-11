#!/usr/bin/env python
import unittest

import tbl

class TaggerTests(unittest.TestCase):
    def test_small(self):
        # the point of this corpus is to generate a NN -> VB / TO _ rule
        corpus = [('the', 'D'), ('horse', 'N'), ('wants', 'V'), ('to', 'T'), ('race', 'V'),
                  ('the', 'D'), ('race', 'N'), ('happened', 'V'),
                  ('the', 'D'), ('race', 'N'), ('continued', 'V')]
        tagger = tbl.Tagger(corpus)
        self.assertEqual(tagger.tag_word('race'), 'N')
        self.assertEqual(tagger.tag_word('the'), 'D')
        self.assertEqual(len(tagger.transforms), 1)
        self.assertEqual(tagger.transforms[0], tbl.Transform('N', 'V', 'T'))
        self.assertEqual(tagger.tag('the race'), [('the', 'D'), ('race', 'N')])
        self.assertEqual(tagger.tag('to race'), [('to', 'T'), ('race', 'V')])
        self.assertEqual(tagger.tag('the horse continued the race'),
                         [('the', 'D'), ('horse', 'N'), ('continued', 'V'), ('the', 'D'),
                          ('race', 'N')])

if __name__ == '__main__':
    unittest.main()
