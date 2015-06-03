'''
Created on Jun 1, 2015

@author: User
'''
import os

from gensim import models, utils
from numpy import get_include, exp
import pyximport
from spacy.en import English

pyximport.install(setup_args={"script_args":["--compiler=mingw32"], 'include_dirs': [get_include(), os.path.dirname(models.__file__)]}, reload_support=True )
from create_seed_neural_bf_inner import train_sentence_sg
from create_seed_vectors import SEED_VECTOR_FILE_NN_BF, WORD2VEC_POS_BF_MODEL, \
    PATTERN_SPLIT_FILE_EXTEND
from create_seed_vectors.create_seed_neural import Seed_Vector_NN

DEBUG_MODE = False
DEBUG_VERBS = ['plant'] 

class Seed_Vector_NN_BF(Seed_Vector_NN):
    def __init__(self, model_file, pattern_sample_file, window_size, alpha = 0.1, iteration = 50, debug_mode = False, debug_verbs = []):
        Seed_Vector_NN.__init__(self, model_file, pattern_sample_file, window_size, alpha, iteration, debug_mode, debug_verbs)
        
    def _train_sentence_sg(self, prepared_sentence, alpha, target_index, syn0_proto, syn1neg_proto):
        train_sentence_sg(self.model, prepared_sentence, alpha, self.work, target_index, self.window_size, syn0_proto, syn1neg_proto)
        
    def _test_score(self, parsed, target_index, window_size, prototype_vector):
        result = 0
        counter = 0
        for index in xrange(target_index - window_size, target_index + window_size + 1):
            if index < 0 or index >= len(parsed):
                continue
            if parsed[index] in self.model.word2id:
                word2 = self.model.word2id[parsed[index]]
                if index == target_index:
                    result += 1 / (1 + exp(-prototype_vector.dot(self.model.syn0[word2])) )
                elif index < target_index:
                    result += 1 / (1 + exp(-prototype_vector[:self.dim].dot(self.model.syn1neg[word2][self.dim:])) )
                else:
                    result += 1 / (1 + exp(-prototype_vector[self.dim:].dot(self.model.syn1neg[word2][:self.dim])) )
                counter += 1
            
        return result/ counter
    
if __name__ == '__main__':
    
    if not os.path.exists(SEED_VECTOR_FILE_NN_BF):
        t = Seed_Vector_NN_BF(WORD2VEC_POS_BF_MODEL, PATTERN_SPLIT_FILE_EXTEND, 4, debug_mode = DEBUG_MODE, debug_verbs = DEBUG_VERBS)
        t.create_pattern_prototypes()
        utils.pickle(t, SEED_VECTOR_FILE_NN_BF)
    else:
        print 'Unpickle Seed_Vector_NN model from file %s ' % SEED_VECTOR_FILE_NN_BF
        t = utils.unpickle(SEED_VECTOR_FILE_NN_BF)
            
    for method in ['weighted']:
#     for method in ['micro', 'macro', 'weighted']:
        print '===================================================================='
        print 'Test SG-NS F1 for %s' % method
        t.test_pattern_prototypes(average=method)
        print '===================================================================='