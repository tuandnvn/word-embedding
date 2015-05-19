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
import math
import os
import sys
import threading
import time
import json
from types import GeneratorType

import en
from gensim import utils, matutils, models  # utility fnc for pickling, common scipy operations etc
from gensim.models.word2vec import Text8Corpus, Vocab, Word2Vec
from numpy import exp, dot, zeros, outer, random, dtype, float32 as REAL, \
    uint32, seterr, array, uint8, vstack, argsort, fromstring, sqrt, newaxis, \
    ndarray, empty, sum as np_sum, prod, get_include
import numpy
import pyximport
from six import iteritems, itervalues, string_types
import codecs
from six.moves import xrange
pyximport.install(setup_args={"script_args":["--compiler=mingw32"], 'include_dirs': [get_include(), os.path.dirname(models.__file__)]}, reload_support=True )
from word2vec_bf_retrain_inner import train_sentence_sg, FAST_VERSION





try:
    from queue import Queue
except ImportError:
    from Queue import Queue

print FAST_VERSION

logger = logging.getLogger("gensim.models.word2vec")


class Word2Vec_BF_Retrain(Word2Vec):
    def __init__(self, initiate_model, prototypes, sentences=None, size=100, alpha=0.001, window=5, min_count=5,
        sample=0, seed=1, workers=1, min_alpha=0.0001, negative=5, hashfxn=hash, iter=1 
        ):
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
        `initiate_model` = the model that used for initiating vectors
        `prototypes` = Prototype is { target_word -> {pattern_no : vector} }
        """
        Word2Vec.__init__(self, sentences, size, alpha, window, min_count, sample, seed, workers, min_alpha, 1, 0, negative, 0, hashfxn, iter)
        
        '''self.prototypes[target_word][pattern_no]'''
        self.initiate_model = initiate_model
        self.prototypes = prototypes
#         self.save_prototype_text('1.txt')
        
        self.index2word = initiate_model.index2word
        self.prototype_index2word = {}
        self.vocab = initiate_model.vocab
        self.prototype_vocab = {}
        self.table = initiate_model.table
        
        self._add_prototype_vocab()
        self.precalc_sampling()
        self.reset_weights()
        
    def save_prototype_text(self, text_file):
        with codecs.open(text_file, 'w', 'utf-8') as file_handler:
            for target_word in self.prototypes:
                file_handler.write(target_word)
                file_handler.write('\n')
                for pattern_no in self.prototypes[target_word]:
                    file_handler.write(pattern_no)
                    file_handler.write('\n')
                    file_handler.write(str(self.prototypes[target_word][pattern_no]))
                    file_handler.write('\n')
        
        
    def _add_prototype_vocab(self):
        '''
        self.target_forms are all inflections forms of verbs in prototypes
        target_form -> target_word
        ate-v -> eat 
        '''
        self.target_forms = {}
        
        no_prototypes = 0
        for target_word in self.prototypes:
            target_word_w_pos = target_word + '-v'
            if target_word_w_pos in self.vocab:
                for pattern_no in self.prototypes[target_word]:
                    if any([math.isnan(val) for val in self.prototypes[target_word][pattern_no]]):
                        print 'NaN value at %s pattern %d' % (target_word , pattern_no)
                        continue 
                    combined_word = target_word + '-' + pattern_no
                    self.prototype_vocab[combined_word] = Vocab(count=self.vocab[target_word_w_pos].count)
                    self.prototype_vocab[combined_word].index = no_prototypes
                    self.prototype_index2word[no_prototypes] = combined_word
                    no_prototypes += 1
            
            '''Add into target_forms'''
#             print 'target_word %s has %d patterns' % ( target_word, len(self.prototypes[target_word]) ) 
            
            self.target_forms[target_word + '-v'] = target_word
            try:
                self.target_forms[en.verb.present(target_word, person = 3) + '-v'] = target_word
            except KeyError:
                self.target_forms[target_word + 's-v'] = target_word
            
            try:
                self.target_forms[en.verb.past_participle(target_word) + '-v'] = target_word
            except KeyError:
                self.target_forms[target_word + 'ed-v'] = target_word
            
            try:
                self.target_forms[en.verb.present_participle(target_word) + '-v'] = target_word
            except KeyError:
                pass
        self.no_prototypes = no_prototypes
        
        print 'Total number of prototypes is %d' %  self.no_prototypes
    
    def reset_weights(self):
        """Reset all projection weights to an initial state from seeding model, but keep the existing vocabulary."""
        logger.info("resetting layer weights")
        self.syn0 = self.initiate_model.syn0
        self.syn0prime = empty( (self.no_prototypes, self.layer1_size), dtype=REAL)
        for target_word in self.prototypes:
            target_word_w_pos = target_word + '-v'
            if target_word_w_pos in self.vocab:
                for pattern_no in self.prototypes[target_word]:
                    combined_word = target_word + '-' + pattern_no
                    index = self.prototype_vocab[combined_word].index
                    self.syn0prime[index] = self.prototypes[target_word][pattern_no]
        self.syn1neg = self.initiate_model.syn1neg
        self.syn0norm = None
        
    def _get_job_words(self, alpha, work, job, neu1):
        return sum(self.select_train_sentence_sg(sentence, alpha, work) for sentence in job)
    
    def update_prototype_to_current(self):
        self.prototypes = {}
        for combined_word in self.prototype_vocab:
            target_word, pattern_no = combined_word.split('-')
            index = self.prototype_vocab[combined_word].index
            if target_word not in self.prototypes:
                self.prototypes[target_word] = {}
            self.prototypes[target_word][pattern_no] = self.syn0prime[index]
            
    def save_prototype(self, prototype_file):
        prototype_copy = {}
        for target_word in self.prototypes:
            prototype_copy[target_word] = {}
            for pattern_no in self.prototypes[target_word]:
                prototype_copy[target_word][pattern_no] = list([float(t) for t in self.prototypes[target_word][pattern_no]])
            
        with codecs.open(prototype_file, 'w', 'utf-8') as file_handler:
            json.dump(prototype_copy, file_handler)
            
    def select_train_sentence_sg(self, sentence, alpha, work):
        target_indexes = []
        for i in range(len(sentence)):
            word = sentence[i]
            if word is None:
                continue
            word_form = self.index2word[word.index]
            if word_form in self.target_forms:
                target_indexes.append(i)
        
        tempo = []
        for target_index in target_indexes:
            average_vector = numpy.zeros(self.layer1_size)
            '''Inflection'''
            word_form = self.index2word[sentence[target_index].index]
            '''Target word'''
            target_word = self.target_forms[word_form]
            
            for index in xrange(target_index - self.window, target_index + self.window + 1):
                if index < 0 or index >= len(sentence):
                    continue
                if sentence[index] is None:
                    continue
                word_index = sentence[index].index
                
                if index == target_index:
                    average_vector += self.syn0[word_index]
                if index < target_index:
                    average_vector[:self.layer1_size/2] += self.syn0[word_index][self.layer1_size/2:] 
                if index > target_index:
                    average_vector[self.layer1_size/2:] += self.syn0[word_index][:self.layer1_size/2]
            
            values = [(p, average_vector.dot(self.prototypes[target_word][p])) for p in self.prototypes[target_word].keys() ]
#             values = [(p, average_vector.dot(self.syn0prime[self.prototype_vocab[target_word + '-' + p].index])) for p in self.prototypes[target_word].keys() if target_word + '-' + p in self.prototype_vocab]
            values = sorted( values, key=lambda x : x[1] )
            
            '''Always select best choice'''
#             if len(values) > 0:
#                 best_pattern = values[-1][0]
#                 combined_word = target_word + '-' + best_pattern
#             
#                 if combined_word in self.prototype_vocab:
#                     sentence[target_index] = self.prototype_vocab[combined_word]
#                     tempo.append(target_index)
            
            '''Select best choice if the second choice is much inferior to the best choice'''
            if len(values) > 1:
                best_pattern = values[-1][0]
                combined_word = target_word + '-' + best_pattern
                
                best_value = values[-1][1]
                second_best_value = values[-2][1]
                if best_value / second_best_value > 1.1 and combined_word in self.prototype_vocab:
                    sentence[target_index] = self.prototype_vocab[combined_word]
                    tempo.append(target_index)
        
        target_indexes = numpy.array(tempo)
#         print target_indexes
#         t = [sentence[i].index for i in target_indexes]
#         print t[:10]

#         t = [self.prototype_index2word[sentence[i].index] for i in target_indexes]
#         print t[:20]

#         target_indexes = numpy.array([6])
#         print 'Outhere %f' % self.syn0prime[2310][0]
        u = train_sentence_sg(self, sentence, target_indexes, alpha, work)
#         print 'Outhere %f' % self.syn0prime[2310][0]
        return u
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
