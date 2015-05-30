'''
Created on May 14, 2015

@author: Tuan Do
'''
import codecs
import json
import os

import numpy

from create_seed_vectors import PATTERN_FILE, PATTERN_SPLIT_FILE, TRAIN, TEST, \
    PDEV_DIR, PATTERN_FILE_EXTEND, PATTERN_SPLIT_FILE_EXTEND
from create_seed_vectors.create_seed import PATTERN, IMPLICATURE, EXAMPLES, \
    PERCENTAGE, PATTERN_NUMBER


def statistics(pattern_sample_file):
    with open(pattern_sample_file, "r") as filehandler:
        data = json.load(filehandler)
    
#     for pattern in data['aim']:
#         no, examples, p = (pattern[PATTERN_NUMBER], pattern[EXAMPLES], pattern[PATTERN])
#         print 'Pattern %s %s' % (no , p)
#         print 'Example'
#         print examples[0]
#         print '----------------------------'
        
    total_target = len(data.keys())
    total_pattern = 0
    total_examples = 0
    for target_word in data:
        no_of_patterns = len(data[target_word])
        examples = 0
        for pattern in data[target_word]:
            examples += len(pattern[EXAMPLES])
        total_pattern += no_of_patterns
        total_examples += examples
         
        print 'Target = %s; pattern = %s; examples = %s ' % (target_word, no_of_patterns, examples)
     
    print 'Total target = %s; total pattern = %s; total examples = %s ' % (total_target, total_pattern, total_examples)

def split_one_verb(data, target_word, multiple_patterns, training_keep):
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
            
            if len(examples) < 5:
                print 'Skip %s ; examples %d; percentage %f' % (pattern[PATTERN_NUMBER], len(examples), percentage)
                continue
            index_counter += 1
        
        if index_counter < 2:
            return
        
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
            
            if len(examples) < 5:
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
                
def split_pattern_file(pattern_sample_file, output_file, training_keep=0.8):
    multiple_patterns = {}
    multiple_patterns[TRAIN] = {}
    multiple_patterns[TEST] = {}
    
    with open(pattern_sample_file, "r") as filehandler:
        data = json.load(filehandler)
        for target_word in data:
            split_one_verb(data, target_word, multiple_patterns, training_keep)
                
    with open(output_file, "w") as filehandler:
        json.dump(multiple_patterns, filehandler)

def print_train_statistics(pattern_sample_file):
    with open(pattern_sample_file, "r") as filehandler:
        pattern_data = json.load(filehandler)
        
    print 'Training statistics'
    
    total_target = len(pattern_data[TRAIN].keys())
    total_pattern = 0
    total_examples = 0
    for target_word in pattern_data[TRAIN]:
        examples = 0
        for pattern in pattern_data[TRAIN][target_word]:
            _, example = (pattern[PATTERN_NUMBER], pattern[EXAMPLES])
            examples += len(example)
        total_examples += examples
        total_pattern += len(pattern_data[TRAIN][target_word])
        
        print 'Target = %s; pattern = %s; examples = %s ' % (target_word, len(pattern_data[TRAIN][target_word]), examples)
        
    print 'Total target = %s; total pattern = %s; total examples = %s ' % (total_target, total_pattern, total_examples)
    
def print_test_statistics(pattern_sample_file):
    with open(pattern_sample_file, "r") as filehandler:
        pattern_data = json.load(filehandler)
    print 'Testing statistics'
    
    total_target = len(pattern_data[TEST].keys())
    total_pattern = 0
    total_examples = 0
    for target_word in pattern_data[TEST]:
        examples = 0
        for pattern in pattern_data[TEST][target_word]:
            _, example = (pattern[PATTERN_NUMBER], pattern[EXAMPLES])
            examples += len(example)
        total_examples += examples
        total_pattern += len(pattern_data[TRAIN][target_word])
            
        print 'Target = %s; pattern = %s; examples = %s ' % (target_word, len(pattern_data[TEST][target_word]), examples)
    print 'Total target = %s; total pattern = %s; total examples = %s ' % (total_target, total_pattern, total_examples)
        
def update_data(additional_pattern_sample_file, processed_file, training_keep=0.8):
    '''When there is a need for updating some verbs because the crawling step has problem'''
    with open(processed_file, "r") as filehandler:
        multiple_patterns = json.load(filehandler)
    
    with codecs.open(additional_pattern_sample_file, "r", 'utf-8') as filehandler:
        data = json.load(filehandler)
        for target_word in data:
            split_one_verb(data, target_word, multiple_patterns, training_keep)
            
    with open(processed_file, "w") as filehandler:
        json.dump(multiple_patterns, filehandler)
                            
if __name__ == '__main__':
#     split_pattern_file(PATTERN_FILE, PATTERN_SPLIT_FILE)
#     update_data(os.path.join(PDEV_DIR, "corpus_call_fixed.json"), PATTERN_SPLIT_FILE)
    statistics(PATTERN_FILE_EXTEND)
    print_train_statistics(PATTERN_SPLIT_FILE_EXTEND)
    print_test_statistics(PATTERN_SPLIT_FILE_EXTEND)