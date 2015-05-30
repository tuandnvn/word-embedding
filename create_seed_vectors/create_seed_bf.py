'''
Created on May 25, 2015

@author: Tuan Do
'''
import os

from gensim import utils
import numpy

from create_seed_vectors import TRAIN, REMOVING_STRS, SEED_VECTOR_FILE_BF, \
    WORD2VEC_POS, PATTERN_SPLIT_FILE, WORD2VEC_POS_BF, SEED_VECTOR_2_FILE, \
    PATTERN_SPLIT_FILE_EXTEND
from create_seed_vectors.create_seed import Seed_Vector, PATTERN, PATTERN_NUMBER, \
    EXAMPLES, LEFT, TARGET, RIGHT, DEBUG_MODE, DEBUG_VERBS, parse_sentence


class Seed_BF_Vector(Seed_Vector):
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
    
    def _process_sentence(self, target_word, sentence, window_size):
        
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
        
        '''Compensate for pos-tagger error'''
        for index, token_w_pos in enumerate(parsed):    
            if token_w_pos == target_word + '-n' or token_w_pos == target_word + '-j':
                target_index = index
                break
        
        if DEBUG_MODE:
            print '-----------'
            print target_word
            print parsed
            print target_index
            
        average_vector = numpy.zeros(self.dim)
        if target_index == -1:
            return average_vector
        
        for index in xrange(target_index - window_size, target_index + window_size + 1):
            if index < 0 or index >= len(parsed):
                continue
            word = parsed[index]
            
#             if word in self.vector_data:
#                 average_vector += self.vector_data[word]
            if word in self.vector_data:
                if index == target_index:
                    average_vector  += self.vector_data[word]
                elif index < target_index:
                    average_vector[:self.dim/2] += self.vector_data[word][self.dim/2:]
                else:
                    average_vector[self.dim/2:] += self.vector_data[word][:self.dim/2]
        
        result = average_vector/ numpy.linalg.norm(average_vector)
        
        if DEBUG_MODE:
            print sentence
            print result[:10]
            
        return result
    
if __name__ == '__main__':
    if DEBUG_MODE:
        t = Seed_BF_Vector(WORD2VEC_POS_BF, PATTERN_SPLIT_FILE_EXTEND, 4, True)
        t.read_pattern()
        t.read_vector_file()
        t.create_pattern_prototypes()
    else:
        if not os.path.exists(SEED_VECTOR_2_FILE):
            print 'Creating Seed_Vector model'
            t = Seed_BF_Vector(WORD2VEC_POS_BF, PATTERN_SPLIT_FILE_EXTEND, 4, True)
            t.read_pattern()
        #     t.baseline_pattern()
              
            t.read_vector_file()
            t.create_pattern_prototypes()
            utils.pickle(t, SEED_VECTOR_2_FILE)
        else:
            print 'Unpickle Seed_Vector model'
            t = utils.unpickle(SEED_VECTOR_2_FILE)
    
    for method in ['weighted']:
#     for method in ['micro', 'macro', 'weighted']:
        print '===================================================================='
        print 'Test SG-NS F1 for %s' % method
        t.test_pattern_prototypes(average=method)
        print '===================================================================='
        