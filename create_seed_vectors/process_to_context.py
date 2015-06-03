'''
Created on Jun 2, 2015

@author: User
'''
import codecs
import json

from create_seed_vectors import TRAIN, TEST, COREFERENCE, DEPENDENCY, TEXT, \
    TOKENS, TREE
from create_seed_vectors.create_seed import PATTERN_NUMBER, FULL_EXAMPLE


class Process_2_Context(object):
    '''
    Process from dependency parsed sentence to its context.
    '''


    def __init__(self, pattern_sample_file, dependency_input_file):
        '''
        Constructor
        '''
        self.pattern_sample_file = pattern_sample_file
        self.dependency_input_file = dependency_input_file
        
    def load_input(self):
        print 'Read pattern file'
        with open(self.pattern_sample_file, "r") as filehandler:
            self.pattern_data = json.load(filehandler)
            
        with codecs.open(self.dependency_input_file, 'r' ,'utf-8') as file_handler:
            self.dependency_data = json.load(file_handler)
            
    def create_context(self):
        if self.debug_mode:
            target_words = self.debug_verbs
        else:
            target_words = self.pattern_data[TRAIN]
            
        for target_word in target_words:
            for pattern in self.pattern_data[TRAIN][target_word] + self.pattern_data[TEST][target_word]:
                pattern_no, full_examples = (pattern[PATTERN_NUMBER], pattern[FULL_EXAMPLE])
                for index, full_example in enumerate(full_examples):
                    key = '_'.join([target_word, pattern_no, str(index)])
                    if key in self.dependency_data:
                        self.create_context_for_key(key, target_word)
        
    def create_context_for_key(self, key, target_word):
        parsed = self.dependency_data[key]
                        
        coref, dependency, text, tokens, tree = parsed[COREFERENCE], parsed[DEPENDENCY], parsed[TEXT], parsed[TOKENS], parsed[TREE]
        
        target_index = -1
        for i, token in enumerate(tokens):
            if token[3] == target_word:
                target_index = i
        '''ROOT is 0'''
        if target_index != -1:
            target_index += 1
            
            left_c = set()
            right_c = set()
            
            right_c_prep = []
            
            for dep in dependency:
                if int(dep[3]) == target_index and dep[0] == 'nsubj':
                    left_c.add(int(dep[4]) - 1)
                if int(dep[3]) == target_index and dep[0] in ['nsubjpass', 'dobj'] :
                    right_c.add(int(dep[4]) - 1)
            
            for dep in dependency:    
                if int(dep[3]) in left_c and dep[0] == 'prep_of':
                    left_c.add(int(dep[4]) - 1)
                
                if int(dep[3]) in right_c and dep[0] == 'prep_of':
                    right_c.add(int(dep[4]) - 1)
            
            l_conj = []
            for dep in dependency:
                if int(dep[4]) == target_index and dep[0] in ['ccomp', 'xcomp' ,'conj_and']:
                    l_conj.append(int(dep[3]) - 1)
                
            if len(l_conj) != 0:
                for dep in dependency:
                    if int(dep[3]) in l_conj and dep[0] == 'nsubj':
                        left_c.add(int(dep[4]) - 1)
                    if int(dep[3]) in l_conj and dep[0] in ['nsubjpass', 'dobj'] :
                        right_c.add(int(dep[4]) - 1)
                        
            for dep in dependency:
                if int(dep[3]) in right_c and dep[0] == 'conj_and':
                    right_c.add(int(dep[4]) - 1)
                if int(dep[3]) in right_c and dep[0] == 'prep_in':
                    right_c_prep.append('in')
                    right_c.add(int(dep[4]) - 1)
            
                if int(dep[3]) in right_c and dep[0] == 'prep_on':
                    right_c_prep.append('on')
            