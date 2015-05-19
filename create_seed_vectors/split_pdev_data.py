'''
Created on May 14, 2015

@author: Tuan Do
'''
import json

import numpy

from create_seed_vectors import PATTERN_FILE, PATTERN_SPLIT_FILE, TRAIN, TEST
from create_seed_vectors.create_seed import PATTERN, IMPLICATURE, EXAMPLES, \
    PERCENTAGE, PATTERN_NUMBER


def split_pattern_file(pattern_sample_file, output_file, training_keep=0.8):
    multiple_patterns = {}
    multiple_patterns[TRAIN] = {}
    multiple_patterns[TEST] = {}
    
    with open(pattern_sample_file, "r") as filehandler:
        data = json.load(filehandler)
        for target_word in data:
            no_of_patterns = len(data[target_word])
            print '%s %d' % (target_word, no_of_patterns)
            
            if no_of_patterns > 1:
                index_counter = 0
                for pattern in data[target_word]:
                    examples = pattern[EXAMPLES]
                    try:
                        percentage = float(pattern[PERCENTAGE])
                    except  ValueError:
                        percentage = 0.0
                    
                    if len(examples) < 5 or percentage < 0.2:
                        print 'Skip %s ; examples %d; percentage %f' % (pattern[PATTERN_NUMBER], len(examples), percentage)
                        continue
                    index_counter += 1
                
                if index_counter < 2:
                    continue
                
                multiple_patterns[TRAIN][target_word] = []
                multiple_patterns[TEST][target_word] = []
                
                train = multiple_patterns[TRAIN][target_word]
                test = multiple_patterns[TEST][target_word]
                
                index_counter = 0    
                for pattern in data[target_word]:
                    examples = pattern[EXAMPLES]
                    try:
                        percentage = float(pattern[PERCENTAGE])
                    except  ValueError:
                        percentage = 0.0
                    
                    if len(examples) < 5 or percentage < 0.2:
                        print 'Skip %s ; examples %d; percentage %f' % (pattern[PATTERN_NUMBER], len(examples), percentage)
                        continue
                    
                    permuted = numpy.random.permutation(len(examples))
                    no_of_training = int(len(permuted) * training_keep)
                    train_examples = [p for i, p in enumerate(pattern[EXAMPLES]) if i in permuted[: no_of_training]]
                    test_examples = [p for i, p in enumerate(pattern[EXAMPLES]) if i in permuted[no_of_training:]]
                    print 'Examples %d; percentage %f; train = %d; test = %d' % (len(examples), percentage, len(train_examples), len(test_examples))
                    
                    train.append({})
                    test.append({})
                    
                    train[index_counter][PATTERN], train[index_counter][IMPLICATURE],\
                     train[index_counter][PATTERN_NUMBER], train[index_counter][EXAMPLES] = \
                     pattern[PATTERN], pattern[IMPLICATURE], pattern[PATTERN_NUMBER], train_examples
                    
                    test[index_counter][PATTERN], test[index_counter][IMPLICATURE],\
                     test[index_counter][PATTERN_NUMBER], test[index_counter][EXAMPLES] = \
                     pattern[PATTERN], pattern[IMPLICATURE], pattern[PATTERN_NUMBER], test_examples
                     
                    index_counter += 1
            else:
                print 'No processing %d samples ' % len(data[target_word][0][EXAMPLES])
                
    with open(output_file, "w") as filehandler:
        json.dump(multiple_patterns, filehandler)
                            
if __name__ == '__main__':
    split_pattern_file(PATTERN_FILE, PATTERN_SPLIT_FILE)
