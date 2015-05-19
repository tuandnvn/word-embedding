'''
Created on May 15, 2015

@author: Tuan Do
'''
"""
Deep learning via word2vec's "skip-gram and CBOW models", using either
hierarchical softmax or negative sampling [1]_ [2]_.
The training algorithms were originally ported from the C package https://code.google.com/p/word2vec/
and extended with additional functionality.
For a blog tutorial on gensim word2vec, with an interactive web app trained on GoogleNews, visit http://radimrehurek.com/2014/02/word2vec-tutorial/
**Make sure you have a C compiler before installing gensim, to use optimized (compiled) word2vec training**
(70x speedup compared to plain NumPy implemenation [3]_).
Initialize a model with e.g.::
>>> model = Word2Vec(sentences, size=100, window=5, min_count=5, workers=4)
Persist a model to disk with::
>>> model.save(fname)
>>> model = Word2Vec.load(fname)  # you can continue training with the loaded model!
The model can also be instantiated from an existing file on disk in the word2vec C format::
  >>> model = Word2Vec.load_word2vec_format('/tmp/vectors.txt', binary=False)  # C text format
  >>> model = Word2Vec.load_word2vec_format('/tmp/vectors.bin', binary=True)  # C binary format
You can perform various syntactic/semantic NLP word tasks with the model. Some of them
are already built-in::
  >>> model.most_similar(positive=['woman', 'king'], negative=['man'])
  [('queen', 0.50882536), ...]
  >>> model.doesnt_match("breakfast cereal dinner lunch".split())
  'cereal'
  >>> model.similarity('woman', 'man')
  0.73723527
  >>> model['computer']  # raw numpy vector of a word
  array([-0.00449447, -0.00310097,  0.02421786, ...], dtype=float32)
and so on.
If you're finished training a model (=no more updates, only querying), you can do
  >>> model.init_sims(replace=True)
to trim unneeded model memory = use (much) less RAM.
Note that there is a :mod:`gensim.models.phrases` module which lets you automatically
detect phrases longer than one word. Using phrases, you can learn a word2vec model
where "words" are actually multiword expressions, such as `new_york_times` or `financial_crisis`:
>>> bigram_transformer = gensim.models.Phrases(sentences)
>>> model = Word2Vec(bigram_transformed[sentences], size=100, ...)
.. [1] Tomas Mikolov, Kai Chen, Greg Corrado, and Jeffrey Dean. Efficient Estimation of Word Representations in Vector Space. In Proceedings of Workshop at ICLR, 2013.
.. [2] Tomas Mikolov, Ilya Sutskever, Kai Chen, Greg Corrado, and Jeffrey Dean. Distributed Representations of Words and Phrases and their Compositionality.
       In Proceedings of NIPS, 2013.
.. [3] Optimizing word2vec in gensim, http://radimrehurek.com/2013/09/word2vec-in-python-part-two-optimizing/
"""

from copy import deepcopy
import heapq
import logging
import os
import sys
import threading
import time
from types import GeneratorType

from gensim import utils, matutils, models  # utility fnc for pickling, common scipy operations etc
from gensim.models.word2vec import Text8Corpus, Vocab, Word2Vec
from numpy import exp, dot, zeros, outer, random, dtype, float32 as REAL, \
    uint32, seterr, array, uint8, vstack, argsort, fromstring, sqrt, newaxis, \
    ndarray, empty, sum as np_sum, prod, get_include
import pyximport
from six import iteritems, itervalues, string_types

from six.moves import xrange

pyximport.install(setup_args={"script_args":["--compiler=mingw32"], 'include_dirs': [get_include(), os.path.dirname(models.__file__)]}, reload_support=True )
from word2vec_bf_inner import train_sentence_sg, FAST_VERSION

try:
    from queue import Queue
except ImportError:
    from Queue import Queue

print FAST_VERSION

logger = logging.getLogger("gensim.models.word2vec")


class Word2Vec_BF(Word2Vec):
    def __init__(self, sentences=None, size=100, alpha=0.025, window=5, min_count=5,
        sample=0, seed=1, workers=1, min_alpha=0.0001, negative=5, hashfxn=hash, iter=1):
        """
        Initialize the model from an iterable of `sentences`. Each sentence is a
        list of words (unicode strings) that will be used for training.
        The `sentences` iterable can be simply a list, but for larger corpora,
        consider an iterable that streams the sentences directly from disk/network.
        See :class:`BrownCorpus`, :class:`Text8Corpus` or :class:`LineSentence` in
        this module for such examples.
        If you don't supply `sentences`, the model is left uninitialized -- use if
        you plan to initialize it in some other way.
        `size` is the dimensionality of the feature vectors.
        `window` is the maximum distance between the current and predicted word within a sentence.
        `alpha` is the initial learning rate (will linearly drop to zero as training progresses).
        `seed` = for the random number generator. Initial vectors for each
        word are seeded with a hash of the concatenation of word + str(seed).
        `min_count` = ignore all words with total frequency lower than this.
        `sample` = threshold for configuring which higher-frequency words are randomly downsampled;
            default is 0 (off), useful value is 1e-5.
        `workers` = use this many worker threads to train the model (=faster training with multicore machines).
        `negative` = if > 0, negative sampling will be used, the int for negative
        specifies how many "noise words" should be drawn (usually between 5-20).
        `hashfxn` = hash function to use to randomly initialize weights, for increased
        training reproducibility. Default is Python's rudimentary built in hash function.
        `iter` = number of iterations (epochs) over the corpus.
        """
        Word2Vec.__init__(self, sentences, size, alpha, window, min_count, sample, seed, workers, min_alpha, 1, 0, negative, 0, hashfxn, iter)

    def _get_job_words(self, alpha, work, job, neu1):
        return sum(train_sentence_sg(self, sentence, alpha, work) for sentence in job)

# Example: ./word2vec.py ~/workspace/word2vec/text8 ~/workspace/word2vec/questions-words.txt ./text8
if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s : %(threadName)s : %(levelname)s : %(message)s', level=logging.INFO)
    logging.info("running %s" % " ".join(sys.argv))
    logging.info("using optimization %s" % FAST_VERSION)

    # check and process cmdline input
    program = os.path.basename(sys.argv[0])
    if len(sys.argv) < 2:
        print(globals()['__doc__'] % locals())
        sys.exit(1)
    infile = sys.argv[1]
    from gensim.models.word2vec import Word2Vec  # avoid referencing __main__ in pickle

    seterr(all='raise')  # don't ignore numpy errors

    # model = Word2Vec(LineSentence(infile), size=200, min_count=5, workers=4)
    model = Word2Vec(Text8Corpus(infile), size=200, min_count=5, workers=1)

    if len(sys.argv) > 3:
        outfile = sys.argv[3]
        model.save(outfile + '.model')
        model.save_word2vec_format(outfile + '.model.bin', binary=True)
        model.save_word2vec_format(outfile + '.model.txt', binary=False)

    if len(sys.argv) > 2:
        questions_file = sys.argv[2]
        model.accuracy(sys.argv[2])

    logging.info("finished running %s" % program)
