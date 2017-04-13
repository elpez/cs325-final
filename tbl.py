import re
from collections import defaultdict, namedtuple, Counter
from operator import itemgetter
from functools import lru_cache
from itertools import product

class Tagger:
    tagset = ()

    def __init__(self, tagged_corpus):
        """Initialize a tagger on the training corpus. This may take a while."""
        self.known_tags = {}
        counted = Counter(tagged_corpus)
        for word, _ in tagged_corpus:
            if word not in self.known_tags:
                tag_counts = ((tag, count) for (w, tag), count in counted.items() if w == word)
                tag, _ = max(tag_counts, key=itemgetter(1))
                self.known_tags[word] = tag
        self.transforms = []
        score_threshold = len(tagged_corpus) * 0.01
        training_corpus = self.apply_ml_tag(word for word, _ in tagged_corpus)
        # generate an immutable set of all possible transforms
        all_transforms = frozenset(Transform(*trp) for trp in product(self.tagset, repeat=3) 
                                                           if trp[0] != trp[1])
        while True:
            transform, score = self.best_transform(training_corpus, tagged_corpus, all_transforms)
            if transform is not None and score < score_threshold:
                self.transforms.append(transform)
                training_corpus = transform(training_corpus)
            else:
                break

    def tag(self, text):
        """Add part-of-speech tags to the text. The argument can be a list of words or a string. If
           the latter, Tagger.process_string will be applied to it to get a list. The return value
           will be a list of (word, tag) pairs.
        """
        if isinstance(text, str):
            text = self.process_string(text)
        tagged_text = self.apply_ml_tag(text)
        for transform in self.transforms:
            tagged_text = transform(tagged_text)
        return tagged_text

    def apply_ml_tag(self, text):
        """Apply the most likely tag to each word in a text."""
        return [(word, self.most_likely_tag(word)) for word in text]

    def most_likely_tag(self, word):
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
    def best_transform(cls, tagged_text, correct_tags, all_transforms):
        """Given a tagged text and its correct tags, return the pair (transform, count), where
           transform is the best transformation to apply from the all_transforms set and count is 
           the number of changes it makes.
        """
        best_so_far = (None, cls.compare_texts(correct_tags, tagged_text))
        for transform in all_transforms:
            transformed = transform(tagged_text)
            score = cls.compare_texts(correct_tags, transformed)
            if score < best_so_far[1]:
                best_so_far = (transform, score)
        return best_so_far

    @staticmethod
    def process_string(s):
        """Turn a string into a list of words, suitable to be passed to the apply_ml_tag method."""
        # put spaces around "n't" so that it gets split
        s = s.replace("n't", " n't ")
        # split on whitespace, commas, and periods, capturing the latter two
        words = re.split(r'\s|(,)|(\.[^0-9])', s)
        # return all non-empty words, with whitespace removed
        return [word.strip() for word in words if word]


class Transform(namedtuple('Transform', ['orig', 'new', 'before'])):
    def mutate(self, tagged_text):
        """Transform the text (a mutable sequence of word-tag pairs) in-place.  Note that the 
           'before' member of the transform is checked against the transformed text, so for example 
           NN -> VB / NN applied to NN NN NN becomes NN VB NN and not NN VB VB.
        """
        prev_tag = None
        for i, (word, tag) in enumerate(tagged_text):
            if prev_tag == self.before and tag == self.orig:
                tagged_text[i] = (word, self.new)
                prev_tag = self.new
            else:
                prev_tag = tag

    def __call__(self, tagged_text):
        """Same as mutate, except return the result instead of modifying the argument."""
        prev_tag = None
        ret = []
        for word, tag in tagged_text:
            if prev_tag == self.before and tag == self.orig:
                ret.append((word, self.new))
                prev_tag = self.new
            else:
                ret.append((word, tag))
                prev_tag = tag
        return ret

    def __str__(self):
        return '{0.orig} -> {0.new} / {0.before} _'.format(self)

def tagged_text_to_str(tagged_text):
    """Convenience function to turn a tagged text into a readable string."""
    return '  '.join('{} ({})'.format(word, tag) for word, tag in tagged_text)
