'''
Created on May 25, 2015

@author: Tuan Do
'''
import os

from gensim import utils
import numpy
from sklearn.metrics.metrics import f1_score, confusion_matrix

from create_seed_vectors import TRAIN, REMOVING_STRS, WORD2VEC_POS, \
    PATTERN_SPLIT_FILE_EXTEND, SEED_VECTOR_FILE_EXTEND, TEST
from create_seed_vectors.create_seed import Seed_Vector, FULL_EXAMPLE, PATTERN, \
    PATTERN_NUMBER, EXAMPLES, LEFT, TARGET, RIGHT, f_score_two_labels, \
    parse_sentence


DEBUG_MODE = False
DEBUG_VERBS = ['scratch']

class Seed_Vector_Extend(Seed_Vector):
    '''
    classdocs
    '''

    def __init__(self, vector_file, pattern_sample_file, window_size, vector_binary = True, margin = 1.0 ):
        '''
        two_component_vector_file:
        A file in the same format as word2vec vector
        
        pattern_sample_file:
        '''
        Seed_Vector.__init__(self, vector_file, pattern_sample_file, window_size, vector_binary, margin)
    
    def test_pattern_prototypes(self, average='weighted'):
        print '===============Test pattern prototypes==============='
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
                pattern_no, examples, full_examples = (pattern[PATTERN_NUMBER], pattern[EXAMPLES], pattern[FULL_EXAMPLE])
#                 if len(full_examples) != len(examples):
#                     print 'full_examples %d; examples %d ' % (len(full_examples), len(examples) )
                if len(examples) > most_frequent:
                    most_frequent = len(examples)
                    most_frequent_no = pattern_no
                weight += len(examples)
                
            for pattern in self.pattern_data[TEST][target_word]:
                pattern_no, examples, full_examples = (pattern[PATTERN_NUMBER], pattern[EXAMPLES], pattern[FULL_EXAMPLE])
                if DEBUG_MODE:
                    print '============Pattern no %s===============' % pattern_no
                    
                for i in xrange(len(examples)):
                    example = examples[i]
                    full_example = full_examples[i]
                    
                    sentence = ' '.join([example[LEFT], example[TARGET], example[RIGHT]])
                    average_vector = self._process_sentence(example[TARGET], sentence)
                    topic_vector = self._process_topic(example[TARGET], full_example)
                    
                    if DEBUG_MODE:
                        print '============Sentence===============\n%s\n' % sentence
                        print '============Full===============\n%s\n' % full_example
                    
#                     sample_vector = numpy.hstack((average_vector, topic_vector))
#                     values = [(p, sample_vector.dot(self.normalized_prototypes[target_word][p] )) for p in self.prototypes[target_word].keys()]
                    values = [(p, average_vector.dot(self.normalized_prototypes[target_word][p][:self.dim] )) for p in self.prototypes[target_word].keys()]
                    
                    values = sorted( values, key=lambda x : x[1] )
                    best = values[-1][0]
                    second_best = values[-2][0]
                    
                    best_value = values[-1][1]
                    second_best_value = values[-2][1]
                    
                    if 'margin' not in self.__dict__:
                        self.margin = 1.0
                    
                    if second_best_value == 0 or best_value / second_best_value > self.margin:
                        y_true.append(int(pattern_no))
                        y_pred.append(int(best))
                    else:
                        values = [(p, topic_vector.dot(self.normalized_prototypes[target_word][p][self.dim:] )) for p in self.prototypes[target_word].keys()]
                        values = sorted( values, key=lambda x : x[1] )
                        new_best = values[-1][0]
                        new_second_best = values[-2][0]
                         
                        new_best_value = values[-1][1]
                        new_second_best_value = values[-2][1]
                        if new_second_best_value == 0 or new_best == second_best and new_second_best == best and new_best_value / new_second_best_value > self.margin:
                            print 'Detect an interesting case best = %s, second_best = %s' % (best, second_best)
                            y_true.append(int(pattern_no))
                            y_pred.append(int(new_best))
                        else:
                            y_true.append(int(pattern_no))
                            y_pred.append(int(best))
                    
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
                print ','.join(['%3d' %t for t in y_true])
                print ','.join(['%3d' %t for t in y_pred])
                print 'Target word: %s ; F1 = %f' % (target_word, score)
                
                labels = sorted(list(set(y_true).union(set(y_pred))))
                print 'Labels  %s' % labels
                t = numpy.array(confusion_matrix(y_true, y_pred, labels), dtype = float)
                print 'Confusion matrix '
                print t
                '''Normalize by row'''
                t_row = (t.transpose() / numpy.sum(t, axis = 1)).transpose()
                print t_row

                
                di = numpy.diag_indices(len(labels))
                t_row[di] = 0
                t[di] = 0

                raw_max = numpy.unravel_index(numpy.argmax(t),  (len(labels), len(labels)) )
                row_max = numpy.unravel_index(numpy.argmax(t_row),  (len(labels), len(labels)) )

                print 'Most confused based on unnormalized; between pattern %s and pattern %s' % (labels[raw_max[0]], labels[raw_max[1]])
                print 'Most confused based on row; between pattern %s and pattern %s' % (labels[row_max[0]], labels[row_max[1]])
        print 'Average unweighted score %f' % (numpy.average (scores))
        print 'Average weighted score %f' % (numpy.average (scores, weights=weights))
        
    def create_pattern_prototypes(self):
        print 'Create pattern prototypes'
        self.prototypes = {}
        self.normalized_prototypes = {}
        
        counter = 0
        if DEBUG_MODE:
            target_words = DEBUG_VERBS
        else:
            target_words = self.pattern_data[TRAIN]
            
        for target_word in target_words:
            counter += 1
            print 'Create prototype for %s' % target_word
            self.prototypes[target_word] = {}
            self.normalized_prototypes[target_word] = {}
            
            for pattern in self.pattern_data[TRAIN][target_word]:
                pattern_form, pattern_no, examples, full_examples = (pattern[PATTERN],
                            pattern[PATTERN_NUMBER], pattern[EXAMPLES], pattern[FULL_EXAMPLE])
#                 if DEBUG_MODE:
#                     print '============Pattern no %s===============' % pattern_no
                
                average_vector = numpy.zeros(self.dim)
                topic_vector = numpy.zeros(self.dim)
                
                p = pattern_form
                for removing_str in REMOVING_STRS:
                    p = p.replace(removing_str, ' ')
                p = p.lower()
                
                '''Give 1/5 of all example weight to pattern'''
                average_vector += float(len(examples))/5 * self._process_sentence(target_word + 's', p)
                
                for i in xrange(len(examples)):
                    example = examples[i]
                    full_example = full_examples[i]
                    sentence = ' '.join([example[LEFT], example[TARGET], example[RIGHT]])
#                     if DEBUG_MODE:
#                         print '============Sentence===============\n%s\n' % sentence
#                         print '============Full===============\n%s\n' % full_example
                    average_vector += self._process_sentence(example[TARGET], sentence)
                    topic_vector += self._process_topic(example[TARGET], full_example)
                
                '''Unnormalized prototype'''
                self.prototypes[target_word][pattern_no] = numpy.hstack((average_vector, topic_vector))
                
                norm = numpy.linalg.norm(average_vector)
                norm_topic = numpy.linalg.norm(topic_vector)
                if norm != 0:
                    average_vector = average_vector/ norm
                if norm_topic != 0:
                    topic_vector =  topic_vector/ norm
                self.normalized_prototypes[target_word][pattern_no] = numpy.hstack((average_vector, topic_vector))
                if DEBUG_MODE:
                    print 'Prototype %s' % pattern_no
                    print self.normalized_prototypes[target_word][pattern_no][:10]
    
    def _process_topic(self, target_word, sentence):
        parsed = parse_sentence(sentence)
        target_index = -1
        for index, token_w_pos in enumerate(parsed):
            if token_w_pos == target_word + '-v':
                target_index = index
                break
            
        topic_vector = numpy.zeros(self.dim)
        if target_index == -1:
            return topic_vector
        
        if not parsed[target_index] in self.vector_data:
            return topic_vector
        
        values = []
        for index in xrange(len(parsed)):
            word = parsed[index]
            if word in self.vector_data and word in self.vocab:
                values.append( (index, self.vector_data[word].dot(self.vector_data[parsed[target_index]] )))
        
        values = sorted( values, key=lambda x : x[1] )
        
        good_indices = [ value[0] for value in values[-len(values)/3:] ]
        
        if DEBUG_MODE:
            good_words = [parsed[index] for index in good_indices]
            print good_words
        
        for index in good_indices:
            word = parsed[index]
            if word in self.vector_data:
                topic_vector += self.vector_data[word]
        
        return topic_vector/ numpy.linalg.norm(topic_vector)
        
    def _process_sentence(self, target_word, sentence):
        print 'Using Seed_Vector_Extend process sentence'
        '''
        Call from read_pattern_file
        '''
        if 'vector_data' not in self.__dict__:
            print 'Raw vector file is not read. Read vector file %s' % self.vector_file
            self.read_raw_file()
            
        parsed = parse_sentence(sentence)
        target_index = -1
        for index, token_w_pos in enumerate(parsed):
            if token_w_pos == target_word + '-v':
                target_index = index
                break
        
        average_vector = numpy.zeros(self.dim)
        if target_index == -1:
            return average_vector
        
        for index in xrange(target_index - self.window_size, target_index + self.window_size + 1):
            if index < 0 or index >= len(parsed):
                continue
            word = parsed[index]
            if word in self.vector_data:
                average_vector += self.vector_data[word]
                
        return average_vector/ numpy.linalg.norm(average_vector)

if __name__ == '__main__':
    if DEBUG_MODE:
        t = Seed_Vector_Extend(WORD2VEC_POS, PATTERN_SPLIT_FILE_EXTEND, 4, True)
        t.read_pattern()
        t.read_vector_file()
        t.create_pattern_prototypes()
    else:
        if not os.path.exists(SEED_VECTOR_FILE_EXTEND):
            t = Seed_Vector_Extend(WORD2VEC_POS, PATTERN_SPLIT_FILE_EXTEND, 4, True)
            t.read_pattern()
            t.read_vector_file()
            t.create_pattern_prototypes()
            utils.pickle(t, SEED_VECTOR_FILE_EXTEND)
        else:
            print 'Unpickle Seed_Vector model'
            t = utils.unpickle(SEED_VECTOR_FILE_EXTEND)
        
#     for method in ['micro', 'macro', 'weighted']:
    for method in ['weighted']:
        print '===================================================================='
        print 'Test SG-NS F1 for %s' % method
        t.test_pattern_prototypes(average=method)
        print '===================================================================='
    
#     t._process_topic("repaired", u"One day she fell and broke her hip : it was repaired in hospital but she remained in some pain and was even more precarious on her feet")
#     t._process_topic("crushed", u"But when she finally capitulates , consenting to call the sun the moon and see the world as her husband wills it , she seems not crushed but excited . There is a frisson between them as if they have discovered a game of role-playing which both find sexually stimulating")
#     t._process_topic("repairing", u"Science : Breaking even in the name of invention Christine McGourty previews the Edinburgh Science Festival By CHRISTINE MCGOURTY ANEW method of repairing bone fractures using a device like a series of ' plastic chinese lanterns ' has been developed at Heriot-Watt University")