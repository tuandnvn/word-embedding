'''
Created on May 26, 2015

@author: Tuan Do
'''
import json

from create_seed_vectors import PATTERN_SPLIT_FILE_EXTEND, TRAIN, TEST, \
    PATTERN_SPLIT_FILE
from create_seed_vectors.create_seed import PATTERN, PATTERN_NUMBER, EXAMPLES, \
    FULL_EXAMPLE


def print_information(pattern_data, verb):
    print '------------TRAIN-------------'
    for target_word in [verb]:
        for pattern in pattern_data[TRAIN][target_word]:
            print '-----------'
            pattern_form, pattern_no, examples = (pattern[PATTERN],
                        pattern[PATTERN_NUMBER], pattern[EXAMPLES])
            print 'No of examples %d ' % (len(examples))
            print 'Pattern %s' % pattern_no
            print 'pattern_form %s' % pattern_form
#             for example in examples:
#                 print example
     
    print '------------TEST-------------'
    for target_word in [verb]:
        for pattern in pattern_data[TEST][target_word]:
            print '-----------'
            pattern_form, pattern_no, examples = (pattern[PATTERN],
                        pattern[PATTERN_NUMBER], pattern[EXAMPLES])
            print 'No of examples %d ' % (len(examples))
            print 'Pattern %s' % pattern_no
            print 'pattern_form %s' % pattern_form
#             for example in examples:
#                 print example

if __name__ == '__main__':
    with open(PATTERN_SPLIT_FILE, "r") as filehandler:
        pattern_data = json.load(filehandler)
    
    print_information(pattern_data, 'follow')    
    
    print '===================================================================='
    print '===================================================================='
    
    with open(PATTERN_SPLIT_FILE_EXTEND, "r") as filehandler:
        pattern_data = json.load(filehandler)
    
    print_information(pattern_data, 'follow')    
