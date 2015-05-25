'''
Created on May 25, 2015

@author: Tuan Do
'''
import os

from gensim import utils
import numpy

from bnc.bnc_process import parse_sentence
from create_seed_vectors import TRAIN, REMOVING_STRS, SEED_VECTOR_FILE_BF, \
    WORD2VEC_POS, PATTERN_SPLIT_FILE, WORD2VEC_POS_BF
from create_seed_vectors.create_seed import Seed_Vector, PATTERN, PATTERN_NUMBER, \
    EXAMPLES, LEFT, TARGET, RIGHT


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
        
        average_vector = numpy.zeros(2 * self.dim)
        if target_index == -1:
            return average_vector
        
        for index in xrange(target_index - self.window_size, target_index + self.window_size + 1):
            if index < 0 or index >= len(parsed):
                continue
            if index == target_index:
                continue
            word = parsed[index]
            if word in self.vector_data:
                if index < target_index:
                    average_vector[:self.dim] += self.vector_data[word]
                else:
                    average_vector[self.dim:] += self.vector_data[word]
                
        return average_vector/ numpy.linalg.norm(average_vector)
    
    def create_pattern_prototypes(self):
        print 'Create pattern prototypes'
        self.prototypes = {}
        self.normalized_prototypes = {}
        
        counter = 0
        for target_word in self.pattern_data[TRAIN]:
            counter += 1
            print 'Create prototype for %s' % target_word
            self.prototypes[target_word] = {}
            self.normalized_prototypes[target_word] = {}
            
            for pattern in self.pattern_data[TRAIN][target_word]:
                pattern_form, pattern_no, examples = (pattern[PATTERN],
                            pattern[PATTERN_NUMBER], pattern[EXAMPLES])
                
                average_vector = numpy.zeros(2 * self.dim)
                
                p = pattern_form
                for removing_str in REMOVING_STRS:
                    p = p.replace(removing_str, ' ')
                p = p.lower()
                
                '''Give 1/5 of all example weight to pattern'''
                average_vector += float(len(examples))/5 * self._process_sentence(target_word + 's', p)
                
                for example in examples:
                    sentence = ' '.join([example[LEFT], example[TARGET], example[RIGHT]])
                    average_vector += self._process_sentence(example[TARGET], sentence)
                
                '''Unnormalized prototype'''
                self.prototypes[target_word][pattern_no] = average_vector
                
                norm = numpy.linalg.norm(average_vector)
                if norm != 0:
                    self.normalized_prototypes[target_word][pattern_no] = average_vector/ norm

if __name__ == '__main__':
    if not os.path.exists(SEED_VECTOR_FILE_BF):
        print 'Creating Seed_Vector model'
        t = Seed_BF_Vector(WORD2VEC_POS_BF, PATTERN_SPLIT_FILE, 5, True)
        t.read_pattern()
    #     t.baseline_pattern()
          
        t.read_vector_file()
        t.create_pattern_prototypes()
        utils.pickle(t, SEED_VECTOR_FILE_BF)
    else:
        print 'Unpickle Seed_Vector model'
        t = utils.unpickle(SEED_VECTOR_FILE_BF)
    
    for method in ['micro', 'macro', 'weighted']:
        print '===================================================================='
        print 'Test SG-NS F1 for %s' % method
        t.test_pattern_prototypes(average=method)
        print '===================================================================='
        