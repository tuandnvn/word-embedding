'''
Created on May 25, 2015

@author: Tuan Do
'''
import os

from gensim import utils
import numpy

from create_seed_vectors import WORD2VEC_POS_BF, SEED_VECTOR_2_FILE_EXTEND, \
    PATTERN_SPLIT_FILE_EXTEND, TRAIN, TEST
from create_seed_vectors.create_seed import PATTERN, PATTERN_NUMBER, EXAMPLES, \
    FULL_EXAMPLE, parse_sentence
from create_seed_vectors.create_seed_bf import Seed_BF_Vector
from create_seed_vectors.create_seed_extend import Seed_Vector_Extend, \
    DEBUG_MODE


class Seed_Vector_BF_Extend(Seed_Vector_Extend, Seed_BF_Vector):
    '''
    classdocs
    '''

    def __init__(self, vector_file, pattern_sample_file, window_size, vector_binary=True, margin=1.0):
        '''
        two_component_vector_file:
        A file in the same format as word2vec vector
        
        pattern_sample_file:
        '''
        Seed_Vector_Extend.__init__(self, vector_file, pattern_sample_file, window_size, vector_binary, margin)
    
    def _process_sentence(self, target_word, sentence):
        return Seed_BF_Vector._process_sentence(self, target_word, sentence)
    
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
                values.append((index, self.vector_data[word].dot(self.vector_data[parsed[target_index]])))
        
        values = sorted(values, key=lambda x : x[1])
        
        good_indices = [ value[0] for value in values[-len(values) / 2:] ]
#         good_words = [parsed[index] for index in good_indices]
#         print good_words
        
        for index in good_indices:
            word = parsed[index]
            if word in self.vector_data:
                if index == target_index:
                    topic_vector += self.vector_data[word]
                elif index < target_index:
                    topic_vector[:self.dim / 2] += self.vector_data[word][self.dim / 2:]
                else:
                    topic_vector[self.dim / 2:] += self.vector_data[word][:self.dim / 2]
        
        return topic_vector / numpy.linalg.norm(topic_vector)
    
if __name__ == '__main__':
    if DEBUG_MODE:
        t = Seed_Vector_BF_Extend(WORD2VEC_POS_BF, PATTERN_SPLIT_FILE_EXTEND, 5, True)
        t.read_pattern()
        t.read_vector_file()
        t.create_pattern_prototypes()
    else:
        if not os.path.exists(SEED_VECTOR_2_FILE_EXTEND):
            print 'Create Seed_Vector BF Extend model'
            t = Seed_Vector_BF_Extend(WORD2VEC_POS_BF, PATTERN_SPLIT_FILE_EXTEND, 4, True)
            t.read_pattern()
            t.read_vector_file()
            t.create_pattern_prototypes()
            utils.pickle(t, SEED_VECTOR_2_FILE_EXTEND)
        else:
            print 'Unpickle Seed_Vector BF Extend model'
            t = utils.unpickle(SEED_VECTOR_2_FILE_EXTEND)
    
    t.margin = 1.05
# #     print t.margin
    for method in ['weighted']:
#     for method in ['weighted']:
        print '===================================================================='
        print 'Test SG-NS F1 for %s' % method
        t.test_pattern_prototypes(average=method)
        print '===================================================================='
