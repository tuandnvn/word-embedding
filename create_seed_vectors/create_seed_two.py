'''
Created on May 12, 2015

@author: Tuan Do
'''
import json
import os
import struct

from gensim import utils
import numpy

from create_seed_vectors import WORD2VEC_POS, PATTERN_SPLIT_FILE, \
    WORD2VEC_POS_BF, PROTOTYPE_POS_BF, PROTOTYPE_POS_BF_AFTER_RETRAIN, \
    SEED_VECTOR_2_FILE, WORD2VEC_POS_INCOR_50K, WORD2VEC_POS_BF_50K, \
    WORD2VEC_POS_INCOR
from create_seed_vectors.create_seed import Seed_Vector, PATTERN, IMPLICATURE, \
    EXAMPLES, LEFT, TARGET, RIGHT, parse_sentence


class Seed_Vector_Two(Seed_Vector):
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
    
    def _process_sentence(self, target_word, sentence):
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
#                 if index == target_index:
#                     average_vector += self.vector_data[word]
                if index <= target_index:
                    average_vector[:self.dim/2] += self.vector_data[word][self.dim/2:] 
                if index >= target_index:
                    average_vector[self.dim/2:] += self.vector_data[word][:self.dim/2]
                    
        return average_vector/ numpy.linalg.norm(average_vector)

if __name__ == '__main__':
    if not os.path.exists(SEED_VECTOR_2_FILE):
        print 'Creating Seed_Vector_Two model'
        t = Seed_Vector_Two(WORD2VEC_POS_BF, PATTERN_SPLIT_FILE, 5, True)
#         t = Seed_Vector_Two(WORD2VEC_POS_INCOR_50K, PATTERN_SPLIT_FILE, 5, True)
#         t = Seed_Vector_Two(WORD2VEC_POS_INCOR, PATTERN_SPLIT_FILE, 5, True)
        t.read_pattern()
    #     t.baseline_pattern()
        
        t.read_vector_file()
        t.create_pattern_prototypes()
        utils.pickle(t, SEED_VECTOR_2_FILE)
    else:
        print 'Unpickle Seed_Vector_Two model'
        t = utils.unpickle(SEED_VECTOR_2_FILE)
    
#     t.generate_random_prototypes()
#     t.create_pattern_prototypes()
    
#     print t.vector_data['the-dt'][:10]
#     print t.vector_data['in-in'][:10]
#     print t.vector_data['animal-n'][:10]
#     t.save_prototypes(PROTOTYPE_POS_BF)
#     t.load_prototypes(PROTOTYPE_POS_BF_AFTER_RETRAIN)
#     t.test_pattern_prototypes()

    for method in ['micro', 'macro', 'weighted']:
        print '===================================================================='
        print 'Test SG-NS-BF F1 for %s' % method
        t.test_pattern_prototypes(average=method)