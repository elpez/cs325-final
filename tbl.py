import re
from collections import defaultdict, namedtuple, Counter
from operator import itemgetter
from itertools import product
import pickle

import nltk
from nltk.corpus import brown, cess_esp

class Tagger:
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
    """Normalize a single tag from the cess_esp tagset. This just chops off everything after and
       including the first digit.
    """
    for i, c in enumerate(tag):
        if c.isdigit():
            return tag[:i]
    return tag

def percentage_correct(my_tags, correct_tags):
    return 100*(1 - (Tagger.compare_texts(my_tags, correct_tags) / len(correct_tags)))

#print(__main__)
#tagger = Tagger.load('cess.tag')

if __name__ == '__main__':
    corpus = cess_esp.tagged_words()
    cess_tagger = Tagger(corpus)
    cess_tagger.save('cess.tag')
    
CESS_ESP_TAGS = set([u'vsip1s0', u'pp2cp00p', u'Fit', u'px2fs0s0', u'vmii1p0', u'vmip1p0', u'dt0fs0', u'vsif1s0', u'vmsi3s0', u'p0300000', u'Fia', u'vsis1s0', u'nccn000', u'aq0cs0', u'pt0mp000', u'px3mp000', u'px3fs000', u'pr0cp000', u'pp3mp000', u'vap00sm', u'px1mp0p0', u'Z', u'pn0cp000', u'dn0cs0', u'sn.e.1n-SUJ', u'dp1msp', u'dp1mss', u'pr0fp000', u'vmsp2s0', u'nccs000', u'pi0fp000', u'ncmp000', u'aq0fp0', u'px1fs0p0', u'vsip2s0', u'vag0000', u'pp3cn000', u'vmis3p0', u'pd0cs000', u'Faa', u'dp2cps', u'vsn0000', u'ao0mp0', u'px3ns000', u'pp3mpa00', u'p010s000', u'vasi1p0', u'vsis3s0', u'vsp00sm', u'vsip3s0', u'van0000', u'dd0ms0', u'di0fp0', u'vaif1p0', u'X', u'vmii2s0', u'pp2cs00p', u'vmsi3p0', u'dp3mp0', u'pp3cna00', u'pp3csd00', u'vaii1p0', u'vam03s0', u'vmis1p0', u'vsii3p0', u'vmg0000', u'vaip1p0', u'pd0fs000', u'dp1css', u'pd0mp000', u'aq0fpp', u'pp1mp000', u'vmic1p0', u'ao0fs0', u'pp3msa00', u'vmsi1s0', u'vaif3p0', u'vssp1s0', u'pi0fs000', u'vmif3s0', u'sn.e-ATR', u'sn.e-SUJ', u'vasp3s0', u'di0fs0', u'vsg0000', u'vmn0000', u'da0ms0', u'vmp00pf', u'dt0cn0', u'nc00000', u'nccp000', u'vmif1p0', u'vais3s0', u'vmii3p0', u'np0000l', u'np0000o', u'pr0cs000', u'pp2cs000', u'pr0ms000', u'pn0fp000', u'rg', u'px3ms000', u'pp3cpa00', u'np0000p', u'rn', u'aq0fsp', u'vssp3p0', u'pe000000', u'vaip2s0', u'dt0ms0', u'dn0fp0', u'pp2cso00', u'ao0ms0', u'vaif3s0', u'aq00000', u'pd0fp000', u'vmsp3s0', u'ao0fp0', u'dp1mpp', u'vmif2s0', u'W', u'vmip3p0', u'aq0cp0', u'pd0ms000', u'Zm', u'pp3fs000', u'sn.e-CD', u'vmip2p0', u'pp3fsa00', u'vmif1s0', u'pp2csn00', u'dn0cp0', u'vssp2s0', u'sn.co-SUJ', u'ncmn000', u'vsm03s0', u'di0mp0', u'dp1fpp', u'np00000', u'aq0fs0', u'Zp', u'Fz', u'vaic1p0', u'sn.e', u'vmii2p0', u'vmip3s0', u'dp3ms0', u'cc', u'pt000000', u'ncfp000', u'di0cs0', u'vmis2s0', u'sn-SUJ', u'vasi3p0', u'Fat', u'pp3ms000', u'cs', u'vsif3p0', u'pi0cp000', u'dd0mp0', u'Fp', u'vmic1s0', u'Fs', u'vmsp2p0', u'dp3cs0', u'pr0cn000', u'Fx', u'pp3ns000', u'vssi3s0', u'vmic3s0', u'vmsp1s0', u'pp3cno00', u'Fc', u'Fd', u'Fe', u'Fg', u'Fh', u'vmm03s0', u'da0fp0', u'pi0cs000', u'vmsp1p0', u'pn0fs000', u'vmip1s0', u'vsic1s0', u'pp3csa00', u'vmm02s0', u'dp1cps', u'pn0mp000', u'dd0fs0', u'vaif2s0', u'vssi3p0', u'vsii1s0', u'p020s000', u'ncfn000', u'vaip2p0', u'pr0mp000', u'pp1cp000', u'spcms', u'pr000000', u'ncfs000', u'vaip3p0', u'pr0fs000', u'vmp00sm', u'dp3cp0', u'vaii1s0', u'px1fp0p0', u'pd0ns000', u'di0cp0', u'vmic3p0', u'vmsi1p0', u'pt0ms000', u'i', u'vsic2s0', u'vasi3s0', u'vsip3p0', u'pp1csn00', u'da0fs0', u'pp3fpa00', u'aq0cn0', u'vsis3p0', u'Fpa', u'vaii3s0', u'pp3cpd00', u'dd0fp0', u'dn0fs0', u'vmm01p0', u'vaii2s0', u'aq0mp0', u'Fpt', u'px1ms0p0', u'vmip2s0', u'dd0cp0', u'vasp3p0', u'vmp00pm', u'vaip3s0', u'vaii3p0', u'aq0msp', u'vmic2s0', u'vaic3s0', u'dn0mp0', u'p010p000', u'vasp1s0', u'pi0ms000', u'vaip1s0', u'pp1cs000', u'vasi1s0', u'vmis1s0', u'de0cn0', u'p0000000', u'vmif3p0', u'vam02s0', u'ncms000', u'pt0cs000', u'di0ms0', u'vsif3s0', u'vmii3s0', u'vsip1p0', u'pp3fp000', u'I', u'vsic3p0', u'vsii1p0', u'vmii1s0', u'sps00', u'dp1fsp', u'pp2cp000', u'dd0cs0', u'aq0mpp', u'vsii3s0', u'vssp3s0', u'Y', u'aq0ms0', u'pn0ms000', u'pd0cp000', u'da0ns0', u'dp3fs0', u'vmm03p0', u'vssf3s0', u'dn0ms0', u'vaic3p0', u'da0mp0', u'pt0cp000', u'np0000a', u'vmsp3p0', u'pi0mp000', u'dp2css', u'vsic3s0', u'vmis3s0', u'pp1cso00', u'vmp00sf'])
