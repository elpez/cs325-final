import re
from collections import defaultdict, namedtuple, Counter
from operator import itemgetter
from itertools import product
import pickle

import nltk
from nltk.corpus import brown, cess_esp

class Tagger(object):
    def __init__(self, tagged_corpus):
        """Initialize a tagger on the training corpus. This may take a while."""
        tagged_corpus = [(word, normalize_tag(tag)) for word, tag in tagged_corpus]
        cfd = nltk.ConditionalFreqDist(tagged_corpus)
        self.known_tags = dict((word, freq.max()) for word, freq in cfd.items())
        my_corpus = self.tag_most_likely(word for word, _ in tagged_corpus)
        self.transforms = [t for t in self.most_common_transforms(my_corpus, tagged_corpus)
                                   if self.score_transform(t, my_corpus, tagged_corpus) > 0]

    @staticmethod
    def load(fpath):
        with open(fpath, 'rb') as ifsock:
            return pickle.load(ifsock)

    def save(self, fpath):
        with open(fpath, 'wb') as ofsock:
            pickle.dump(self, ofsock)

    def tag(self, text):
        """Add part-of-speech tags to the text. The argument can be a list of words or a string. If
           the latter, Tagger.process_string will be applied to it to get a list. The return value
           will be a list of (word, tag) pairs.

           Make sure you really want this and not tag_normalized.
        """
        if isinstance(text, str):
            text = self.process_string(text)
        tagged_text = self.tag_most_likely(text)
        for transform in self.transforms:
            tagged_text = transform(tagged_text)
        return tagged_text

    def tag_most_likely(self, text):
        """Add the most likely part-of-speech tags to the text based solely on POS frequency."""
        return [(word, self.tag_word(word)) for word in text]

    def tag_word(self, word):
        """Return the most likely POS tag for a word. If the word is not present in the tagger's 
           corpus, 'UNK' is returned.
        """
        return self.known_tags.get(word, 'UNK')

    @staticmethod
    def compare_texts(text1, text2):
        """Return the number of tags for which the tagged texts disagree."""
        pred = lambda zipped: zipped[0][1] != zipped[1][1]
        return len(list(filter(pred, zip(text1, text2))))

    @classmethod
    def all_transforms(cls, my_tagged_text, correct_tagged_text):
        for i, (_, tag) in enumerate(correct_tagged_text[1:], start=1):
            my_tag = my_tagged_text[i][1]
            if my_tag != tag:
                yield Transform(my_tag, tag, my_tagged_text[i-1][1])

    @classmethod
    def most_common_transforms(cls, my_tagged_text, correct_tagged_text, threshold=0.00005):
        c = Counter(cls.all_transforms(my_tagged_text, correct_tagged_text))
        threshold_count = len(correct_tagged_text) * threshold
        for transform, count in c.items():
            if count >= threshold_count:
                yield transform

    @classmethod
    def score_transform(cls, transform, my_tagged_text, correct_tagged_text):
        original_score = cls.compare_texts(my_tagged_text, correct_tagged_text)
        new_score = cls.compare_texts(transform(my_tagged_text), correct_tagged_text)
        return original_score - new_score

    @staticmethod
    def process_string(s):
        """Turn a string into a list of words, suitable to be passed to the tag_most_likely method.
        """
        # put spaces around "n't" so that it gets split
        s = s.replace("n't", " n't ")
        # split on whitespace, commas, and periods, capturing the latter two
        words = re.split(r'\s|(,)|(\.[^0-9])', s)
        # return all non-empty words, with whitespace removed
        return [word.strip() for word in words if word]

class Transform(namedtuple('BaseTransform', ['orig', 'new', 'before'])):
    def __call__(self, tagged_text):
        """Transform the text (a mutable sequence of word-tag pairs) and return the result. Note 
           that the 'before' member of the transform is checked against the transformed text, so for
           example NN -> VB / NN applied to NN NN NN becomes NN VB NN and not NN VB VB.
        """
        tagged_text_copy = tagged_text[:]
        self.mutate(tagged_text_copy)
        return tagged_text_copy

    def mutate(self, tagged_text):
        """Same as __call__, except the text is modified in-place."""
        prev_tag = None
        for i, (word, tag) in enumerate(tagged_text):
            if prev_tag == self.before and tag == self.orig:
                tagged_text[i] = (word, self.new)
                prev_tag = self.new
            else:
                prev_tag = tag

    def __str__(self):
        return '{0.orig} -> {0.new} / {0.before} _'.format(self)

def tagged_text_to_str(tagged_text):
    """Convenience function to turn a tagged text into a readable string."""
    return '  '.join('{} ({})'.format(word, tag) for word, tag in tagged_text)

def normalize_tag(tag):
    """Normalize a single tag from the cess_esp tagset. This just chops off the semantic annotation.
    """
    #return tag[0] #this would remove everything except the basic POS
    return tag.partition('00')[0]

def percentage_correct(my_tags, correct_tags):
    return 100*(1 - (Tagger.compare_texts(my_tags, correct_tags) / len(correct_tags)))

# load the taggers from file
brown_tagger = Tagger.load('brown.tag')
cess_tagger = Tagger.load('cess.tag')
