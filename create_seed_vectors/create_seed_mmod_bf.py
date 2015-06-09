'''
Created on Jun 3, 2015

@author: Tuan Do
'''
import os
import random

from gensim import utils
import numpy
from scipy.cluster.vq import vq, kmeans, whiten
from sklearn.metrics.metrics import f1_score, confusion_matrix

from cluster.method.kmeans import KMeansClustering
from create_seed_vectors import TRAIN, SEED_VECTOR_MMOD_FILE, WORD2VEC_POS_BF, \
    PATTERN_SPLIT_FILE_EXTEND, TEST
from create_seed_vectors.create_seed import DEBUG_MODE, DEBUG_VERBS, \
    PATTERN_NUMBER, EXAMPLES, LEFT, TARGET, RIGHT, f_score_two_labels
from create_seed_vectors.create_seed_bf import Seed_BF_Vector


class Seed_Mmod_BF_Vector(Seed_BF_Vector):
    '''
    classdocs
    '''

    def __init__(self, vector_file, pattern_sample_file, window_size, split_threshold, vector_binary = True, margin = 1.0, cluster_try = 5 ):
        '''
        Constructor
        '''
        Seed_BF_Vector.__init__(self, vector_file, pattern_sample_file, window_size, vector_binary, margin)
        self.split_threshold = split_threshold
        self.cluster_try = cluster_try
        
    def fit_pattern_prototypes(self, average='weighted'):
        print 'Test pattern prototypes'
        scores = []
        weights = []
        
        if DEBUG_MODE:
            target_words = DEBUG_VERBS
        else:
            target_words = self.pattern_data[TRAIN]
        
#         target_words = ['allocate']
        
        for target_word in target_words:
            self.delete_fitted(target_word)
            
        for target_word in target_words:
            score, weight = self.fit_pattern_prototypes_for_verb(target_word, average, 2, do_split_cluster = True)
            scores.append(score)
            weights.append(weight)

        print 'Average unweighted score %f' % (numpy.average (scores))
        print 'Average weighted score %f' % (numpy.average (scores, weights=weights))
        
    def delete_fitted(self, target_word):
        remove_keys = self.prototypes[target_word].keys()
        for pattern_no in remove_keys:
            if len(pattern_no.split('_')) > 1:
                del self.prototypes[target_word][pattern_no]
                del self.normalized_prototypes[target_word][pattern_no]
            
            
    def fit_pattern_prototypes_for_verb(self, target_word, average, cluster_number, do_split_cluster = True, verbose = True):
        y_true = []
        y_pred = []
        weight = 0
        
        most_frequent_no = -1
        most_frequent = 0
        
        data = {}
        
        for pattern in self.pattern_data[TRAIN][target_word]:
            pattern_no, examples = (pattern[PATTERN_NUMBER], pattern[EXAMPLES])
            if len(examples) > most_frequent:
                most_frequent = len(examples)
                most_frequent_no = int(pattern_no)
            weight += len(examples)
            
        for pattern in self.pattern_data[TRAIN][target_word]:
            pattern_no, examples = (pattern[PATTERN_NUMBER], pattern[EXAMPLES])
            data[int(pattern_no)] = numpy.zeros((len(examples), self.dim), dtype=numpy.float64)
            for index, example in enumerate(examples):
                sentence = ' '.join([example[LEFT], example[TARGET], example[RIGHT]])
                average_vector = self._process_sentence(example[TARGET], sentence, self.window_size)
                
                data[int(pattern_no)][index] = average_vector
                
                values = [(p, average_vector.dot(self.normalized_prototypes[target_word][p])) for p in self.prototypes[target_word].keys()]
                values = sorted(values, key=lambda x : x[1])
                
                best = values[-1][0]
                
                best_value = values[-1][1]
                
                if best_value != 0:
                    y_true.append(int(pattern_no))
                    
                    if len(best.split('_')) > 1:
                        best_label = best.split('_')[0]
                    else:
                        best_label = best
                        
                    y_pred.append(int(best_label))
#                     print '%s %s %s' %(int(pattern_no), best, int(best_label))
                elif best_value == 0:
                    average_vector = self._process_sentence(example[TARGET], sentence, 2 * self.window_size)
                    values = [(p, average_vector.dot(self.normalized_prototypes[target_word][p])) for p in self.prototypes[target_word].keys()]
                    values = sorted(values, key=lambda x : x[1])
                    best = values[-1][0]
                    y_true.append(int(pattern_no))
                    if len(best.split('_')) > 1:
                        best_label = best.split('_')[0]
                    else:
                        best_label = best
                    y_pred.append(int(best_label))
                
                if DEBUG_MODE:
                    print '-- Example is of pattern %s, classified as %s' % (pattern_no, best)
                        
            weight += len(examples)
        
        score = None
        if len(set(y_true)) == 2 and most_frequent_no in set(y_true):
            score = f_score_two_labels(y_true, y_pred, average=average)
        elif len(set(y_true)) > 2:
            score = f1_score(y_true, y_pred, average=average)
        print score
        
        if score != None:        
            print '---------'
            if verbose:
                print ','.join(['%3d' % t for t in y_true])
                print ','.join(['%3d' % t for t in y_pred])
            print 'Target word: %s ; F1 = %f' % (target_word, score)
            
            labels = sorted(list(set(y_true).union(set(y_pred))))
            if verbose:
                print 'Labels  %s' % labels
            t = numpy.array(confusion_matrix(y_true, y_pred, labels), dtype=float)
            if verbose:
                print 'Confusion matrix '
                print t
            '''Normalize by row'''
            t_row = (t.transpose() / numpy.sum(t, axis=1)).transpose()
            if verbose:
                print t_row
            
            di = numpy.diag_indices(len(labels))
            diag = t_row[di]
            need_to_split = numpy.where (diag < self.split_threshold) [0]
            
            t_row[di] = 0
            t[di] = 0

            raw_max = numpy.unravel_index(numpy.argmax(t), (len(labels), len(labels)))
            row_max = numpy.unravel_index(numpy.argmax(t_row), (len(labels), len(labels)))
            
            if verbose:
                print 'Most confused based on unnormalized; between pattern %s and pattern %s' % (labels[raw_max[0]], labels[raw_max[1]])
                print 'Most confused based on row; between pattern %s and pattern %s' % (labels[row_max[0]], labels[row_max[1]])
            
            if do_split_cluster and len(need_to_split) > 0 and cluster_number < 3:
                print '-------SPLIT--------'
                print 'Labels needs to be split are ' + ' '.join([str(labels[value]) for value in need_to_split])
                
                all_clusters = []
                all_clustes_scores = []
                original_score = score
                for split_index, value in enumerate(need_to_split):
                    all_clusters.append([])
                    all_clustes_scores.append([])
                    
                    p = labels[value]
                    print 'Split label %s into %s clusters' % (p, cluster_number) 
                    
                    for tr in xrange(self.cluster_try):
                        print '-- Try %s' % tr
                        whitened = whiten(data[p])
                        seed_index = range(len(whitened))
                        random.shuffle(seed_index)
                        seed_index = seed_index[:cluster_number]
                        
                        cluster_seeds = whitened[seed_index]
                        clusters, _ = kmeans(whitened, cluster_seeds)
                        all_clusters[split_index].append(clusters)
                        
                        for i, cluster in enumerate(clusters):
                            average_vector = cluster
                            new_pattern_no = str(p) + '_' + str(i)
                            norm = numpy.linalg.norm(average_vector)
                            
                            if norm != 0:
                                self.prototypes[target_word][new_pattern_no] = average_vector
                                self.normalized_prototypes[target_word][new_pattern_no] = average_vector / norm
                        
                        score, _ = self.fit_pattern_prototypes_for_verb(target_word, average, cluster_number + 1, do_split_cluster = True, verbose = False)
                        
                        all_clustes_scores[split_index].append(score)
                        
                        self.delete_fitted(target_word)
                
                print '----- Select the best clustering -----'
                print all_clustes_scores
                for split_index in xrange(len(all_clustes_scores)):
                    p = labels[need_to_split[split_index]]
                    argmax = numpy.argmax(all_clustes_scores[split_index])
                    best_score = all_clustes_scores[split_index][argmax]
                    if best_score > original_score:
                        print 'Split %s based on the %s\'th clustering' % (p, argmax) 
                        best_cluster = all_clusters[split_index][argmax]
                        for i, cluster in enumerate(best_cluster):
                            average_vector = cluster
                            new_pattern_no = str(p) + '_' + str(i)
                            print 'Cluster %s is %s' % (i, average_vector[:10])
                            norm = numpy.linalg.norm(average_vector)
                            
                            if norm != 0:
                                self.prototypes[target_word][new_pattern_no] = average_vector
                                self.normalized_prototypes[target_word][new_pattern_no] = average_vector / norm
                    
                print '------------Retest with optimal configuration---------------'
                score, _ = self.fit_pattern_prototypes_for_verb(target_word, average, cluster_number + 1, do_split_cluster = False, verbose = True)
                
            return (score, weight)
        else:
            print score
            
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
                    average_vector = self._process_sentence(example[TARGET], sentence, self.window_size)
                    values = [(p, average_vector.dot(self.normalized_prototypes[target_word][p])) for p in self.prototypes[target_word].keys()]
                    values = sorted(values, key=lambda x : x[1])
                    best = values[-1][0]
                    
                    best_value = values[-1][1]
                    
                    if best_value != 0:
                        y_true.append(int(pattern_no))
                        
                        if len(best.split('_')) > 1:
                            best_label = best.split('_')[0]
                        else:
                            best_label = best
                        y_pred.append(int(best_label))
                    elif best_value == 0:
                        average_vector = self._process_sentence(example[TARGET], sentence, 2 * self.window_size)
                        values = [(p, average_vector.dot(self.normalized_prototypes[target_word][p])) for p in self.prototypes[target_word].keys()]
                        values = sorted(values, key=lambda x : x[1])
                        best = values[-1][0]
                        y_true.append(int(pattern_no))
                        if len(best.split('_')) > 1:
                            best_label = best.split('_')[0]
                        else:
                            best_label = best
                        y_pred.append(int(best_label))
                    
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

        print 'Average unweighted score %f' % (numpy.average (scores))
        print 'Average weighted score %f' % (numpy.average (scores, weights=weights))
        
if __name__ == '__main__':
    if not os.path.exists(SEED_VECTOR_MMOD_FILE):
        print 'Creating Seed_Vector model'
        t = Seed_Mmod_BF_Vector(WORD2VEC_POS_BF, PATTERN_SPLIT_FILE_EXTEND, 4, 0.7)
        t.read_pattern()
    #     t.baseline_pattern()
          
        t.read_vector_file()
        t.create_pattern_prototypes()
        utils.pickle(t, SEED_VECTOR_MMOD_FILE)
    else:
        print 'Unpickle Seed_Vector model'
        t = utils.unpickle(SEED_VECTOR_MMOD_FILE)
    
    t.split_threshold = 0.7
    t.cluster_try = 1
    t.fit_pattern_prototypes(average='weighted')
    utils.pickle(t, SEED_VECTOR_MMOD_FILE)
    t.test_pattern_prototypes(average = 'weighted')