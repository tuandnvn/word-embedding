'''
Created on Jun 2, 2015

@author: User
'''
import codecs
import json
import math
import os
from pprint import PrettyPrinter

from create_seed_vectors import TRAIN, TEST, COREFERENCE, DEPENDENCY, TEXT, \
    TOKENS, TREE, PATTERN_SPLIT_FILE_EXTEND, DEPENDENCY_FILE, DEPENDENCY_FILE_2
from create_seed_vectors.create_seed import PATTERN_NUMBER, FULL_EXAMPLE, \
    PATTERN, EXAMPLES

prepositions = ['in', 'on', 'with', 'into', 'at', 'above', 'from', 
                'within', 'before',  'under', 'between', 'as', 'since', 'to',
                'against', 'during', 'over', 'upon', 'behind', 'after', 'up', 'down',
                'through', 'along', 'across', 'to']

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
        self.load_input()
        
    def load_input(self):
        print 'Read pattern file'
        with open(self.pattern_sample_file, "r") as filehandler:
            self.pattern_data = json.load(filehandler)
        print 'Finish reading pattern'
        
        print 'Read dependency file'
        with codecs.open(self.dependency_input_file, 'r' ,'utf-8') as file_handler:
            self.dependency_data = json.load(file_handler)
        print 'Finish reading dependency'
            
    def create_context(self):
        if self.debug_mode:
            target_words = self.debug_verbs
        else:
            target_words = self.pattern_data[TRAIN]
            
        for target_word in target_words:
            for pattern in self.pattern_data[TRAIN][target_word]:
                pattern_no, full_examples = (pattern[PATTERN_NUMBER], pattern[FULL_EXAMPLE])
                for index, full_example in enumerate(full_examples):
                    key = '_'.join([target_word, pattern_no, str(index)])
                    if key in self.dependency_data[TRAIN]:
                        self.create_context_for_key(key, target_word, self.dependency_data[TRAIN])
            
            for pattern in self.pattern_data[TEST][target_word]:
                pattern_no, full_examples = (pattern[PATTERN_NUMBER], pattern[FULL_EXAMPLE])
                for index, full_example in enumerate(full_examples):
                    key = '_'.join([target_word, pattern_no, str(index)])
                    if key in self.dependency_data[TEST]:
                        self.create_context_for_key(key, target_word, self.dependency_data[TEST])
            
    
    def create_context_for_all(self):
        keys = self.dependency_data[TRAIN]
        keys = sorted(keys)
        
        v = 'lead'
        ps = {}
        for pattern in self.pattern_data[TRAIN][v]:
            pattern_form, pattern_no = (pattern[PATTERN], pattern[PATTERN_NUMBER]) 
            ps [pattern_no] = pattern_form
        pt_nos = ps.keys()
        pt_nos = sorted(pt_nos)
        for p in pt_nos:
            print '%s %s' % (p, ps[p])
            
        for key in keys:
#             print key
            target_word = key.split('_')[0]
#             print target_word
            if target_word == v:
                self.create_context_for_key(key, target_word, self.dependency_data[TRAIN])
            
    def create_context_for_key(self, key, target_word, data):
        print '-------------%s-------------' % key
        parsed = data[key]
        if parsed == None:
            return
                        
        _, dependency, text, tokens, _ = parsed[COREFERENCE], parsed[DEPENDENCY], parsed[TEXT], parsed[TOKENS], parsed[TREE]
        print text
        target_index = (-1, -1)
        
        for i, sent in enumerate(tokens):
            for j, token in enumerate(sent):
                if token[3] == unicode(target_word):
                    target_index = (i,j)
                    break
            else:
                continue
            break
        '''ROOT is 0'''
        
        if target_index != (-1, -1):
            sent_i = target_index[0]
            token_i = target_index[1]
            
            left_c = set()
            right_c = set()
            
            right_c_prep = []
            
            deps = [(dep[0], dep[1], dep[2], int(dep[3].replace('\'', '')), int(dep[4].replace('\'', ''))) for dep in dependency[sent_i]]
            
            HEAD_INDEX = 3
            DEP_INDEX =  4
            
            def is_target_head(dep):
                return dep[HEAD_INDEX] == token_i + 1
        
            def is_target_dependent(dep):
                return dep[DEP_INDEX] == token_i + 1
            
            def head_in_list(dep, l):
                return dep[HEAD_INDEX] in l
            
            def dep_in_list(dep, l):
                return dep[DEP_INDEX] in l
            
            agents = []
            l_conj = []
            for dep in deps:
                if is_target_head(dep) and dep[0] == 'nsubj':
                    left_c.add(dep[DEP_INDEX])
                if is_target_head(dep) and dep[0] in ['nsubjpass', 'dobj', 'acomp'] :
                    right_c.add(dep[DEP_INDEX])
                if is_target_head(dep) and dep[0] in ['dep'] :
                    if abs(dep[HEAD_INDEX] - dep[DEP_INDEX]) < 5:
                        right_c.add(dep[DEP_INDEX])
                        
                if is_target_head(dep) and dep[0] == 'agent':
                    agents.append(dep[DEP_INDEX])
                    
                if is_target_dependent(dep) and dep[0] in [u'conj_and']:
                    l_conj.append(dep[HEAD_INDEX])
                    
                if is_target_dependent(dep) and dep[0] in ['relcl'] :
                    if tokens[sent_i][token_i][4] == 'VBN':
                        right_c.add(dep[HEAD_INDEX])
                    else:
                        left_c.add(dep[HEAD_INDEX])
            
            if len(agents) != 0:
                for dep in deps:
                    if head_in_list(dep, agents) and dep[0] == 'pobj':
                        left_c.add(dep[4])
                        
            if len(l_conj) != 0:
                for dep in deps:
                    if head_in_list(dep, l_conj) and dep[0] in ['nsubj']:
                        left_c.add(dep[4])
                    if head_in_list( dep, l_conj) and dep[0] in ['nsubjpass'] :
                        right_c.add(dep[4])
                        
            l_conj = set()
            l_conj.add(token_i + 1)
            
            '''Nested deep == 2'''
            for i in xrange(2):
#                 print 'Loop %s %s ' % (i, l_conj)
                xcomp = set()
                for dep in deps:
                    if dep_in_list(dep, l_conj) and dep[0] in [u'xcomp']:
                        l_conj.add(dep[HEAD_INDEX])
                        xcomp.add(dep[HEAD_INDEX])
                        
                if len(xcomp) != 0:
#                     print 'xcomp %s' % xcomp
                    for dep in deps:
                        object_marked = []
                        if head_in_list(dep, xcomp) and dep[0] in ['dobj']:
                            print 'dep[DEP_INDEX] %s' % dep[DEP_INDEX]
                            left_c.add(dep[DEP_INDEX])
                            object_marked.append(dep[HEAD_INDEX])
                    for dep in deps:
                        if head_in_list(dep, xcomp) and dep[HEAD_INDEX] not in object_marked and dep[0] in ['nsubj', 'nsubjpass']:
                            print 'dep[DEP_INDEX] %s' % dep[DEP_INDEX]
                            left_c.add(dep[DEP_INDEX])
                
                vmod = set()        
                for dep in deps:
                    if dep_in_list(dep, l_conj) and dep[0] in [u'vmod']:
                        head = dep[HEAD_INDEX] - 1
                        if tokens[sent_i][head][4][:2] == 'NN':
                            if tokens[sent_i][token_i][4] == 'VBG':
                                left_c.add(dep[3])
                            if tokens[sent_i][token_i][4] in ['VBN', 'VB']:
                                right_c.add(dep[3])
                        elif tokens[sent_i][head][4][:2] == 'VB':
                            l_conj.add(dep[3])
                            vmod.add(dep[3])
                            
                if len(vmod) != 0:
                    print 'vmod %s' % vmod
                    for dep in deps:
                        if head_in_list(dep, vmod) and dep[0] in ['nsubj', 'nsubjpass']:
                            print 'dep[DEP_INDEX] %s' % dep[DEP_INDEX]
                            left_c.add(dep[DEP_INDEX])
            
            left_ofs = []
            right_ofs = []
            for dep in deps:   
                if head_in_list(dep, left_c) and (dep[0], dep[2]) == ('prep', 'of'):
                    left_ofs.append(dep[DEP_INDEX])
                
                if head_in_list(dep, right_c) and (dep[0], dep[2]) == ('prep', 'of'):
                    right_ofs.append(dep[DEP_INDEX])
                    
            if len(left_ofs) != 0:
                for dep in deps:
                    if head_in_list(dep, left_ofs) and dep[0] == 'pobj':
                        left_c.add(dep[4])
            if len(right_ofs) != 0:
                for dep in deps:
                    if head_in_list(dep, right_ofs) and dep[0] == 'pobj':
                        right_c.add(dep[4])
            
            right_c_p_word = []
            for dep in deps:
                if head_in_list(dep, right_c) and dep[0] == 'conj_and':
                    right_c.add(dep[4])
                    
                if is_target_head(dep) and dep[0] in ['advmod', 'npadvmod', 'npmod']:
                    right_c_p_word.append(dep[DEP_INDEX])
                
                if (head_in_list(dep, right_c) or is_target_head(dep))  and dep[0] == 'prep' and dep[2] in prepositions:
                    right_c_prep.append(dep[DEP_INDEX])
                    
                if head_in_list(dep, right_c_prep)   and dep[0] == 'prep' and dep[2] in prepositions:
                    right_c_prep.append(dep[DEP_INDEX])
                    
            for dep in deps:
                if head_in_list(dep, right_c_prep) and dep[0] == 'pobj':
                    right_c_p_word.append(dep[DEP_INDEX])
                    
            r_conj = set()
            for dep in deps:
                if int(dep[3]) == token_i + 1 and dep[0] in [u'ccomp', u'xcomp', u'prt', u'advcl', u'advmod:']:
                    r_conj.add(dep[4])
                    
            left_c = [(sent_i, t) for t in left_c]
            right_c = [(sent_i, t) for t in right_c]
            r_conj = [(sent_i, t) for t in r_conj]
            right_c_p_word = [(sent_i, t) for t in right_c_p_word] 
            right_c_prep_word = [(sent_i, t) for t in right_c_prep]
            
            left_c_words = [tokens[i][j-1][0] for (i,j) in left_c]
            right_c_words = [tokens[i][j-1][0] for (i,j) in right_c]
            r_conj_words = [tokens[i][j-1][0] for (i,j) in r_conj]
            right_c_p_words = [tokens[i][j-1][0] for (i,j) in right_c_p_word]
            right_c_prep_words = [tokens[i][j-1][0] for (i,j) in right_c_prep_word] 
            print left_c_words
            print right_c_words
            print right_c_prep_words
            print right_c_p_words
            print r_conj_words
            return 
        else:
            return ([], [])
        
    def check_covering(self):
        for data_type in [TRAIN, TEST]:
            total_counter = 0
            total_parsed_counter = 0
            for target_word in sorted(self.pattern_data[data_type].keys()):
                counter = 0
                parsed_counter = 0
                for pattern in self.pattern_data[data_type][target_word]:
                    pattern_no, examples = (pattern[PATTERN_NUMBER], pattern[EXAMPLES])
                    for i in xrange(len(examples)):
                        key = '%s_%s_%s' % (target_word, pattern_no, i)
                        if key in self.dependency_data[data_type] and self.dependency_data[data_type][key] != None:
                            parsed_counter += 1
                    
                    counter += len(examples)
                    
                total_counter += counter
                total_parsed_counter += parsed_counter
                print 'Covering for %s is %s / %s' % (target_word, parsed_counter, counter)
        
            print 'Covering for all %s is %s / %s' % (data_type, total_parsed_counter, total_counter)
    
    def save_dep_for_one_word(self, target_word, output, readable_output):
        data = {TRAIN:{}, TEST:{}}
        for data_type in [TRAIN, TEST]:
            for pattern in self.pattern_data[data_type][target_word]:
                pattern_no, examples = (pattern[PATTERN_NUMBER], pattern[EXAMPLES])
                for i in xrange(len(examples)):
                    key = '%s_%s_%s' % (target_word, pattern_no, i)
                    if key in self.dependency_data[data_type]:
                        data[data_type][key] = self.dependency_data[data_type][key]
        
        with codecs.open(output, 'w', 'utf-8') as file_handler:
            json.dump(data, file_handler)
        with codecs.open(readable_output, 'w', 'utf-8') as file_handler:
            pp = PrettyPrinter(width=200, stream = file_handler)
            pp.pprint(data)
            
if __name__ == '__main__':
#     t = Process_2_Context(PATTERN_SPLIT_FILE_EXTEND, DEPENDENCY_FILE)
# #     t.check_covering()
#     t.save_dep_for_one_word('allocate','temp.json', 'temp.txt')
    
#     t = Process_2_Context(PATTERN_SPLIT_FILE_EXTEND, 'temp.json')
#     t.create_context_for_all()
#     t.create_context_for_key('appear_5_4', 'appear', t.dependency_data[TEST])
#     t.create_context_for_key('scratch_3_1', 'scratch', t.dependency_data[TEST])
    
#     t = Process_2_Context(PATTERN_SPLIT_FILE_EXTEND, DEPENDENCY_FILE_2)
#     t.save_dep_for_one_word('allocate', 'allocate.json', 'allocate.txt')
    
    t = Process_2_Context(PATTERN_SPLIT_FILE_EXTEND, 'lead.json')
    t.create_context_for_all()
    