'''
Created on May 29, 2015

@author: Tuan Do
'''
import os

from gensim import utils

from create_seed_vectors import SEED_VECTOR_FILE, WORD2VEC_POS, \
    PATTERN_SPLIT_FILE_EXTEND
from create_seed_vectors.create_seed import Seed_Vector


if __name__ == '__main__':
    if not os.path.exists(SEED_VECTOR_FILE):
        print 'Creating Seed_Vector model'
        t = Seed_Vector(WORD2VEC_POS, PATTERN_SPLIT_FILE_EXTEND, 4, True)
        t.read_pattern()
    #     t.baseline_pattern()
          
        t.read_vector_file()
        t.create_pattern_prototypes()
        utils.pickle(t, SEED_VECTOR_FILE)
    else:
        print 'Unpickle Seed_Vector model'
        t = utils.unpickle(SEED_VECTOR_FILE)
        
    for method in ['micro', 'macro', 'weighted']:
        print '===================================================================='
        print 'Test Baseline F1 for %s' % method
        t.baseline_pattern(average=method)
        print '===================================================================='