'''
Created on Jun 7, 2015

@author: Tuan Do
'''
import codecs
import json
import os

from gensim import utils
import numpy

from create_seed_vectors import COREFERENCE, DEPENDENCY, TEXT, TOKENS, TREE, \
    SEED_VECTOR_2_FILE, WORD2VEC_POS_BF, DEPENDENCY_FILE, \
    PATTERN_SPLIT_FILE_EXTEND, SEED_VECTOR_DEP_BF_FILE, DEPENDENCY_FILE_CLEARNLP
from create_seed_vectors.create_seed import LEFT, TARGET, RIGHT, get_brief_pos,\
    DEBUG_MODE
from create_seed_vectors.create_seed_bf import Seed_BF_Vector
from create_seed_vectors.split_up_json import read_splitted_json_files

prepositions = ['in', 'on', 'with', 'into', 'at', 'above', 'from', 
                'within', 'before',  'under', 'between', 'as', 'since', 'to',
                'against', 'during', 'over', 'upon', 'behind', 'after', 'up', 'down',
                'through', 'along', 'across']


class Seed_Dep_Vector(Seed_BF_Vector):
    '''
    '''

    def __init__(self, vector_file, pattern_sample_file, dependency_input_file, window_size, vector_binary = True, margin = 1.0, input_splited = False ):
        '''
        '''
        Seed_BF_Vector.__init__(self, vector_file, pattern_sample_file, window_size, vector_binary, margin)
        self.dependency_input_file = dependency_input_file
        self.input_splited = input_splited
        self.load_input()
        
    def load_input(self):
        if self.input_splited:
            self.pattern_data = read_splitted_json_files(self.dependency_input_file)
        else:
            print 'Read pattern file %s' % self.pattern_sample_file
            with open(self.pattern_sample_file, "r") as filehandler:
                self.pattern_data = json.load(filehandler)
            print 'Finish reading pattern'
        
        print 'Read vector file %s' % self.vector_file
        self.read_vector_file()
        
        print 'Read dependency file'
        with codecs.open(self.dependency_input_file, 'r' ,'utf-8') as file_handler:
            self.dependency_data = json.load(file_handler)
        print 'Finish reading dependency'
    
    def create_context_for_key(self, key, target_word, data):
        '''
        data should be either self.dependency_data[TRAIN] | self.dependency_data[TEST]
        '''
        print '-------------%s-------------' % key
        if key not in data:
            return
        parsed = data[key]
        if parsed == None:
            return
        
        print 'Key in data OK'
                        
        _, dependency, text, tokens, _ = parsed[COREFERENCE], parsed[DEPENDENCY], parsed[TEXT], parsed[TOKENS], parsed[TREE]
        print text
        target_index = (-1, -1)
        
        for i, sent in enumerate(tokens):
            for j, token in enumerate(sent):
                if token[3] == target_word:
                    target_index = (i,j)
                    break
            else:
                continue
            break
        '''ROOT is 0'''
        
        print target_index
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
            
            for dep in deps:
                if is_target_head(dep) and dep[0] == 'nsubj':
                    left_c.add(dep[DEP_INDEX])
                if is_target_head(dep) and dep[0] in ['nsubjpass', 'dobj', 'acomp'] :
                    right_c.add(dep[DEP_INDEX])
                if is_target_head(dep) and dep[0] in ['dep'] :
                    if abs(dep[HEAD_INDEX] - dep[DEP_INDEX]) < 5:
                        right_c.add(dep[DEP_INDEX])
                    
                if is_target_dependent(dep) and dep[0] in ['rcmod'] :
                    if tokens[sent_i][token_i][4] == 'VBN':
                        right_c.add(dep[HEAD_INDEX])
                    else:
                        left_c.add(dep[HEAD_INDEX])
                        
            l_conj = []
            for dep in deps:
                if is_target_dependent(dep) and dep[0] in [u'conj_and']:
                    l_conj.append(dep[HEAD_INDEX])
                    
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
                            left_c.add(dep[DEP_INDEX])
                            object_marked.append(dep[HEAD_INDEX])
                    for dep in deps:
                        if head_in_list(dep, xcomp) and dep[HEAD_INDEX] not in object_marked and dep[0] in ['nsubj', 'nsubjpass']:
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
                    for dep in deps:
                        if head_in_list(dep, vmod) and dep[0] in ['nsubj', 'nsubjpass']:
                            print 'dep[DEP_INDEX] %s' % dep[DEP_INDEX]
                            left_c.add(dep[DEP_INDEX])
            
            for dep in deps:   
                if head_in_list( dep, left_c) and dep[0] == 'prep_of':
                    left_c.add(dep[DEP_INDEX])
                
                if head_in_list( dep, right_c) and dep[0] == 'prep_of':
                    right_c.add(dep[DEP_INDEX])
                    
            right_c_p_word = []
            for dep in deps:
                if dep[3] in right_c and dep[0] == 'conj_and':
                    right_c.add(dep[4])
                    
                if is_target_head(dep) and dep[0] == 'advmod':
                    right_c_p_word.append(dep[DEP_INDEX])
                    
                for preposition in ['in', 'on', 'with', 'into', 'at', 'above', 'from', 
                                    'within', 'before',  'under', 'between', 'as', 'since', 'to',
                                    'against', 'during', 'over', 'upon', 'such_as', 'behind', 'after',
                                    'through', 'along', 'across']:
                    if (dep[3] in right_c or dep[3] == token_i + 1)  and dep[0] == 'prep_' + preposition:
                        right_c_prep.append(preposition)
                        right_c_p_word.append(dep[4])
                        
                if (dep[3] in right_c or dep[3] == token_i + 1)  and dep[0] == 'prep':
                    right_c_prep.append(tokens[sent_i][dep[4]-1][3])
                    
            r_conj = set()
            for dep in deps:
                if int(dep[3]) == token_i + 1 and dep[0] in [u'ccomp', u'xcomp', u'prt', u'advcl', u'advmod:']:
                    r_conj.add(dep[4])
                    
            left_c = [(sent_i, t) for t in left_c]
            right_c = [(sent_i, t) for t in right_c]
            r_conj = [(sent_i, t) for t in r_conj]
            right_c_p_word = [(sent_i, t) for t in right_c_p_word]
            
            left_with_pos_context = [tokens[i][j-1][0].lower() + '-' + get_brief_pos(tokens[i][j-1][4]) for (i,j) in left_c]
            right_with_pos_context = [tokens[i][j-1][0].lower() + '-' + get_brief_pos(tokens[i][j-1][4]) for (i,j) in right_c + r_conj + right_c_p_word]
            
            left_ne = set([tokens[i][j-1][5].lower() + '-n' for (i,j) in left_c if tokens[i][j-1][5] != u'O'])
            right_ne = set([tokens[i][j-1][5].lower() + '-n' for (i,j) in right_c + r_conj + right_c_p_word if tokens[i][j-1][5] != u'O'])
            
            left_with_pos_context += left_ne
            right_with_pos_context += right_ne
            
            for prep in right_c_prep:
                right_with_pos_context.append(prep + '-in')
            return (tokens[sent_i][token_i][0] + '-v', left_with_pos_context, right_with_pos_context)
        else:
            return None
        
    def create_context_for_key_clearnlp(self, key, target_word, data):
        '''
        data should be either self.dependency_data[TRAIN] | self.dependency_data[TEST]
        '''
        print '-------------%s-------------' % key
        if key not in data:
            return
        parsed = data[key]
        if parsed == None:
            return
        
        print 'Key in data OK'
                        
        _, dependency, text, tokens, _ = parsed[COREFERENCE], parsed[DEPENDENCY], parsed[TEXT], parsed[TOKENS], parsed[TREE]
        print text
        target_index = (-1, -1)
        
        for i, sent in enumerate(tokens):
            for j, token in enumerate(sent):
                if token[3] == target_word:
                    target_index = (i,j)
                    break
            else:
                continue
            break
        '''ROOT is 0'''
        
        print target_index
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
                            left_c.add(dep[DEP_INDEX])
                            object_marked.append(dep[HEAD_INDEX])
                    for dep in deps:
                        if head_in_list(dep, xcomp) and dep[HEAD_INDEX] not in object_marked and dep[0] in ['nsubj', 'nsubjpass']:
                            if tokens[sent_i][token_i][4] == 'VBN':
                                right_c.add(dep[DEP_INDEX])
                            else:
                                left_c.add(dep[DEP_INDEX])
                
                acl = set()        
                for dep in deps:
                    if dep_in_list(dep, l_conj) and dep[0] in [u'acl']:
                        if tokens[sent_i][token_i][4] == 'VBG':
                            left_c.add(dep[3])
                        if tokens[sent_i][token_i][4] in ['VBN', 'VB']:
                            right_c.add(dep[3])
                            
                if len(acl) != 0:
                    for dep in deps:
                        if head_in_list(dep, acl) and dep[0] in ['nsubj', 'nsubjpass']:
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
                    
                if (head_in_list(dep, right_c) or is_target_head(dep))  and dep[0] == 'prep':
                    right_c_prep.append(dep[DEP_INDEX])
                
                '''To handle the case
                Lead up to -> verb prep prep
                '''
                if head_in_list(dep, right_c_prep)   and dep[0] == 'prep':
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
            
            left_with_pos_context = [tokens[i][j-1][0].lower() + '-' + get_brief_pos(tokens[i][j-1][4]) for (i,j) in left_c]
            right_with_pos_context = [tokens[i][j-1][0].lower() + '-' + get_brief_pos(tokens[i][j-1][4]) for (i,j) in right_c + right_c_p_word + right_c_prep_word]
            
            def get_full_ne( ne ):
                if ne == 'ORG':
                    return 'organization-n'
                return ne.lower() + '-n'
            
            left_ne = set([get_full_ne(tokens[i][j-1][5]) for (i,j) in left_c if tokens[i][j-1][5] != u'O'])
            right_ne = set([get_full_ne(tokens[i][j-1][5]) for (i,j) in right_c + r_conj + right_c_p_word if tokens[i][j-1][5] != u'O'])
            
            left_with_pos_context += left_ne
            right_with_pos_context += right_ne
            
            return (tokens[sent_i][token_i][0] + '-v', left_with_pos_context, right_with_pos_context)
        else:
            return None
        
    def _get_average_vector_from(self, example, data_type, key, window_size):
        target_word = key.split('_')[0]
        average_vector = numpy.zeros(self.dim)
        _ = self.create_context_for_key_clearnlp(key, target_word, self.dependency_data[data_type])
        if _ != None:
            parsed_word, left_context, right_context = _ 
            
            if DEBUG_MODE:
                print '-------- CONTEXT ------------'
                print left_context
                print right_context
            if left_context != [] or right_context != []:
                for word in left_context:
                    if word in self.vector_data:
                        average_vector[:self.dim/2] += self.vector_data[word][self.dim/2:]
                for word in right_context:
                    if word in self.vector_data:
                        average_vector[self.dim/2:] += self.vector_data[word][:self.dim/2]
                if parsed_word in self.vector_data:
                    average_vector  += self.vector_data[parsed_word]
                return average_vector
        sentence = ' '.join([example[LEFT], example[TARGET], example[RIGHT]])
        return self._process_sentence(example[TARGET], sentence, window_size)
        
if __name__ == '__main__':
    if not os.path.exists(SEED_VECTOR_DEP_BF_FILE):
        print 'Creating Seed_Vector model'
#         t = Seed_Dep_Vector(WORD2VEC_POS_BF, PATTERN_SPLIT_FILE_EXTEND, 'allocate.json', 4, True)
        t = Seed_Dep_Vector(WORD2VEC_POS_BF, PATTERN_SPLIT_FILE_EXTEND, DEPENDENCY_FILE_CLEARNLP, 4, True)
        t.create_pattern_prototypes()
        utils.pickle(t, SEED_VECTOR_DEP_BF_FILE)
    else:
        print 'Unpickle Seed_Vector model'
        t = utils.unpickle(SEED_VECTOR_DEP_BF_FILE)
    
#     for method in ['weighted']:
    for method in ['micro', 'macro', 'weighted']:
        print '===================================================================='
        print 'Test SG-NS F1 for %s' % method
        t.test_pattern_prototypes(average=method, retest = False)
        print '===================================================================='