'''
Created on May 30, 2015

@author: Tuan Do
'''
from copy import deepcopy
import os
from random import shuffle
import random

from gensim import utils, models
from numpy import zeros, exp, dot, outer, get_include, float32 as REAL
import numpy
import pyximport
from sklearn.metrics.metrics import f1_score, confusion_matrix

pyximport.install(setup_args={"script_args":["--compiler=mingw32"], 'include_dirs': [get_include(), os.path.dirname(models.__file__)]}, reload_support=True )
# pyximport.install(setup_args={'include_dirs': [get_include(), os.path.dirname(models.__file__)]}, reload_support=True )
from create_seed_neural_inner import train_sentence_sg
from create_seed_vectors import TRAIN, REMOVING_STRS, TEST, WORD2VEC_POS_MODEL, \
    PATTERN_SPLIT_FILE_EXTEND
from create_seed_vectors.create_seed import Seed_Vector, DEBUG_MODE, DEBUG_VERBS, \
    PATTERN, PATTERN_NUMBER, EXAMPLES, LEFT, TARGET, RIGHT, parse_sentence, \
    f_score_two_labels


# def train_sg_pair(model, word, word2, alpha, prototype_vector):
#     labels = zeros(model.negative + 1)
#     labels[0] = 1.0
#             
#     l1 = model.syn0[word2]
#     neu1e = zeros(l1.shape)
# 
#     word_indices = [word]
#     while len(word_indices) < model.negative + 1:
#         w = model.table[random.randint(model.table.shape[0])]
#         if w != word:
#             word_indices.append(w)
#     l2b = model.syn1neg[word_indices]  # 2d matrix, k+1 x layer1_size
#     fb = 1. / (1. + exp(-dot(l1, l2b.T)))  # propagate hidden -> output
#     gb = (labels - fb) * alpha  # vector of error gradients multiplied by the learning rate
#     
#     neu1e += dot(gb, l2b)  # save error
#     prototype_vector += neu1e  # learn input -> hidden

class Seed_Vector_NN(Seed_Vector):
    '''
    classdocs
    '''


    def __init__(self, model_file, pattern_sample_file, window_size, alpha = 0.05, iteration = 5):
        '''
        two_component_vector_file:
        A file in the same format as word2vec vector
        
        pattern_sample_file:
        '''
        print "Read model file %s" % model_file
        self.model = utils.unpickle(model_file)
        self.syn0 = self.model.syn0
        self.pattern_sample_file = pattern_sample_file
        self.window_size = window_size
        self.read_pattern()
        self.read_vocab()
        self.alpha = alpha
        self.min_alpha = 0.01
        self.iter = iteration
        self.dim = self.model.layer1_size
        
        self.work = zeros(self.layer1_size, dtype=REAL)
    
    def test_pattern_prototypes(self, average='weighted'):
        print 'Test pattern prototypes'
        scores = []
        weights = []
        
        counter = 0
        
        if DEBUG_MODE:
            target_words = DEBUG_VERBS
        else:
            target_words = self.pattern_data[TRAIN]
            
        for target_word in target_words:
#             if counter > 3:
#                 break
            counter += 1
            y_true = []
            y_pred = []
            weight = 0
            
            most_frequent_no = -1
            most_frequent = 0
            
            for pattern in self.pattern_data[TEST][target_word]:
                pattern_no, examples = (pattern[PATTERN_NUMBER], pattern[EXAMPLES])
                if len(examples) > most_frequent:
                    most_frequent = len(examples)
                    most_frequent_no = pattern_no
                weight += len(examples)
                
            for pattern in self.pattern_data[TEST][target_word]:
                pattern_no, examples = (pattern[PATTERN_NUMBER], pattern[EXAMPLES])
                
                for example in examples:
                    sentence = ' '.join([example[LEFT], example[TARGET], example[RIGHT]])
                    values = [(p, self.test_score(self.normalized_prototypes[target_word][p], example[TARGET], sentence)) for p in self.prototypes[target_word].keys()]
                    values = sorted(values, key=lambda x : x[1])
                    best = values[-1][0]
                    
                    best_value = values[-1][1]
                    
                    if best_value != 0:
                        y_true.append(int(pattern_no))
                        y_pred.append(int(best))
                    elif best_value == 0:
                        y_true.append(int(pattern_no))
                        y_pred.append(most_frequent_no)
                    
                    if DEBUG_MODE:
                        print '-- Example is of pattern %s, classified as %s' % (pattern_no, best)
                            
                weight += len(examples)
            
            score = None
            if len(set(y_true)) == 2 and most_frequent_no in set(y_true):
                score = f_score_two_labels(y_true, y_pred, average=average)
            elif len(set(y_true)) > 2:     
                score = f1_score(y_true, y_pred, average=average)
            
            if score != None:        
                scores.append(score)
                weights.append(weight)
                
                print '---------'
                print ','.join(['%3d' % t for t in y_true])
                print ','.join(['%3d' % t for t in y_pred])
                print 'Target word: %s ; F1 = %f' % (target_word, score)
                
                labels = sorted(list(set(y_true).union(set(y_pred))))
                print 'Labels  %s' % labels
                t = numpy.array(confusion_matrix(y_true, y_pred, labels), dtype=float)
                print 'Confusion matrix '
                print t
                '''Normalize by row'''
                t_row = (t.transpose() / numpy.sum(t, axis=1)).transpose()
                print t_row
                
                di = numpy.diag_indices(len(labels))
                t_row[di] = 0
                t[di] = 0

                raw_max = numpy.unravel_index(numpy.argmax(t), (len(labels), len(labels)))
                row_max = numpy.unravel_index(numpy.argmax(t_row), (len(labels), len(labels)))

                print 'Most confused based on unnormalized; between pattern %s and pattern %s' % (labels[raw_max[0]], labels[raw_max[1]])
                print 'Most confused based on row; between pattern %s and pattern %s' % (labels[row_max[0]], labels[row_max[1]])
#                 '''Normalize by column'''
#                 t_col = t / numpy.sum(t, axis = 0)
#                 print t_col
#                 t_col[di] = 0
#                 col_max = numpy.unravel_index(numpy.argmax(t_col),  (len(labels), len(labels)) )
#                 print 'Most confused based on col; between pattern %s and pattern %s' % (labels[col_max[0]], labels[col_max[1]])

        print 'Average unweighted score %f' % (numpy.average (scores))
        print 'Average weighted score %f' % (numpy.average (scores, weights=weights))
    
    def create_pattern_prototypes(self):
        print 'Create pattern prototypes'
        self.prototypes = {}
        self.c_prototypes = {}
        self.normalized_prototypes = {}
        self.normalized_c_prototypes = {}
        
        counter = 0
        if DEBUG_MODE:
            target_words = DEBUG_VERBS
        else:
            target_words = self.pattern_data[TRAIN]
            
        for target_word in target_words:
            counter += 1
            print 'Create prototype for %s' % target_word
            self.prototypes[target_word] = {}
            self.c_prototypes[target_word] = {}
            self.normalized_prototypes[target_word] = {}
            self.normalized_c_prototypes[target_word] = {}
            
            for pattern in self.pattern_data[TRAIN][target_word]:
                pattern_form, pattern_no, examples = (pattern[PATTERN],
                            pattern[PATTERN_NUMBER], pattern[EXAMPLES])
                if DEBUG_MODE:
                    print '=== Create prototype for pattern %s' % pattern_no
                
                syn0_proto = self.syn0[self.model.word2id[target_word + '-v']]
                syn1neg_proto = self.syn1neg[self.model.word2id[target_word + '-v']]
                
                for i in xrange(self.iter):
                    alpha = max(self.min_alpha, self.alpha * (1 - 1.0 * i / self.iter))
                    p = pattern_form
                    for removing_str in REMOVING_STRS:
                        p = p.replace(removing_str, ' ')
                    p = p.lower()
                    
                    sentences = [(example[TARGET], ' '.join([example[LEFT], example[TARGET], example[RIGHT]])) for example in examples]
                    '''Give 1/4 of all example weight to pattern'''
                    sentences += ((target_word + 's', p) for _ in xrange(len(examples)/4))
                    shuffle(sentences)
                
                    for target, sentence in sentences:
                        self.retrain_vector_sentence(target, sentence, alpha, self.window_size, syn0_proto, syn1neg_proto)
                
                '''Unnormalized prototype'''
                self.prototypes[target_word][pattern_no] = syn0_proto
                self.c_prototypes[target_word][pattern_no] = syn1neg_proto
                
                norm = numpy.linalg.norm(syn0_proto)
                if norm != 0:
                    self.normalized_prototypes[target_word][pattern_no] = syn0_proto / norm
                else:
                    self.normalized_prototypes[target_word][pattern_no] = syn0_proto
                    
                c_norm = numpy.linalg.norm(syn1neg_proto)
                if c_norm != 0:
                    self.normalized_c_prototypes[target_word][pattern_no] = syn1neg_proto / c_norm
                else:
                    self.normalized_c_prototypes[target_word][pattern_no] = syn1neg_proto
                
                
                if DEBUG_MODE:
                    print 'Prototype %s' % pattern_no
                    print self.normalized_prototypes[target_word][pattern_no][:10]
    
    def test_score(self, prototype_vector, target_word, sentence, window_size):
        parsed = parse_sentence(sentence)
        if not target_word + '-v' in self.model.word2id:
            return 0
        
        result = 0
        target_index = -1
        for index, token_w_pos in enumerate(parsed):
            if token_w_pos == target_word + '-v':
                target_index = index
                break
        
        for index, token_w_pos in enumerate(parsed):    
            if token_w_pos == target_word + '-n' or token_w_pos == target_word + '-j':
                target_index = index
                break
        
        for index in xrange(target_index - window_size, target_index + window_size + 1):
            if index < 0 or index >= len(parsed):
                continue
            
            if parsed[index] in self.model.word2id:
                word2 = self.model.word2id[parsed[index]]
                
                result += 1 / (1 + exp(-prototype_vector.dot(self.model.syn1neg[word2])) )
        return result
        
    def retrain_vector_sentence(self, target_word, sentence, alpha, window_size, syn0_proto, syn1neg_proto):
        if 'vector_data' not in self.__dict__:
            print 'Raw vector file is not read. Read vector file %s' % self.vector_file
            self.read_raw_file()
        
        if DEBUG_MODE:
            print 'retrain_vector_sentence %s' % sentence
        parsed = parse_sentence(sentence)
        
        if not target_word + '-v' in self.model.word2id:
            return
            
        target_index = -1
        for index, token_w_pos in enumerate(parsed):
            if token_w_pos == target_word + '-v':
                target_index = index
                break
        
        for index, token_w_pos in enumerate(parsed):    
            if token_w_pos == target_word + '-n' or token_w_pos == target_word + '-j':
                target_index = index
                break
        
        if target_index == -1:
            return
        
        prepared_sentence = [self.model.vocab[word] for word in parsed if word in self.model.vocab]
        
        train_sentence_sg(self.model, prepared_sentence, alpha, self.work, target_index, alpha, self.window_size, syn0_proto, syn1neg_proto)
#         for index in xrange(target_index - window_size, target_index + window_size + 1):
#             if index < 0 or index >= len(parsed):
#                 continue
#             if parsed[index] in self.model.word2id:
#                 word2 = self.model.word2id[parsed[index]]
#             
#                 if word2 in self.syn0:
#                     train_sg_pair(self.model, word2, word, alpha, prototype_vector)
                    

if __name__ == '__main__':
    t = Seed_Vector_NN(WORD2VEC_POS_MODEL, PATTERN_SPLIT_FILE_EXTEND, 4)
    t.create_pattern_prototypes()
    for method in ['weighted']:
#     for method in ['micro', 'macro', 'weighted']:
        print '===================================================================='
        print 'Test SG-NS F1 for %s' % method
        t.test_pattern_prototypes(average=method)
        print '===================================================================='