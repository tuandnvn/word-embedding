'''
Created on May 12, 2015

@author: Tuan Do
'''
import codecs
import json
import struct
import sys

import numpy
from sklearn.metrics import f1_score, precision_score, recall_score, confusion_matrix
from spacy.en import English

from create_seed_vectors import REMOVING_STRS, TRAIN, TEST, WORD2VEC_POS, \
    PATTERN_SPLIT_FILE, WORD2VEC_POS_FRE, WORD2VEC_POS_BF


# 'pattNum' - the pattern number (as a string)
# 'patt' - the pattern
# 'impl' - the implicature
# 'per' - frequency percentage
# 'examples' - a list of examples for this pattern
# Each example in the list is a dictionary with keys: 'left','right','kwic'
PATTERN = 'patt'
PATTERN_NUMBER = 'pattNum'
IMPLICATURE = 'impl'
EXAMPLES = 'examples'
PERCENTAGE = 'per'
LEFT = 'left'
TARGET = 'kwic'
RIGHT = 'right'
SUBJECT = 'subject'
VERB = 'verb'
INDIROBJECT = 'indirobject'
OBJECT = 'object'
COMPLEMENT = 'complement'
ADVERBIALS = 'adverbials'

nlp = English()

def parse_sentence(sentence):
    result = []
    pos_results = nlp(sentence)
    for token_struct in pos_results:
        token, pos = token_struct.orth_, token_struct.tag_
        pos = pos.lower()
        if pos[-1:] == '$':
            pos = pos[:-1]
        if pos[:2] == 'jj':
            pos = 'j'
        if pos[:2] == 'nn':
            pos = 'n'
        if pos[:2] == 'vb':
            pos = 'v'
        if pos[:1] == 'w':
            pos = 'w'
        if pos[:2] == 'rb':
            pos = 'r'
        token = token.lower()
        result.append(token + '-' + pos)
    return result

class Seed_Vector(object):
    '''
    classdocs
    '''

    def __init__(self, vector_file, pattern_sample_file, window_size, vector_binary = True ):
        '''
        two_component_vector_file:
        A file in the same format as word2vec vector
        
        pattern_sample_file:
        '''
        self.vector_file = vector_file
        self.pattern_sample_file = pattern_sample_file
        self.window_size = window_size
        self.vector_binary = vector_binary
    
    def test_pattern_prototypes(self):
        print 'Test pattern prototypes'
        scores = []
        weights = []
        
        counter = 0
#         for target_word in ['appear']:
        for target_word in self.pattern_data[TEST]:
#             if counter > 3:
#                 break
            counter += 1
            y_true = []
            y_pred = []
            weight = 0
            
            most_frequent_no = -1
            most_frequent = 0
            
            for pattern in self.pattern_data[TEST][target_word]:
                pattern_no, examples = (pattern[PATTERN_NUMBER], pattern[EXAMPLES])
                if len(examples) > most_frequent:
                    most_frequent = len(examples)
                    most_frequent_no = pattern_no
                weight += len(examples)
                
            for pattern in self.pattern_data[TEST][target_word]:
                pattern_no, examples = (pattern[PATTERN_NUMBER], pattern[EXAMPLES])
                for example in examples:
                    sentence = ' '.join([example[LEFT], example[TARGET], example[RIGHT]])
                    average_vector = self._process_sentence(example[TARGET], sentence)
                    values = [(p, average_vector.dot(self.prototypes[target_word][p])) for p in self.prototypes[target_word].keys()]
                    values = sorted( values, key=lambda x : x[1] )
                    best = values[-1][0]
                    
                    y_true.append(int(pattern_no))
                    y_pred.append(int(best))
                weight += len(examples)
            
            if len(set(y_true)) == 2:
                score = f1_score(y_true, y_pred, average='micro', pos_label=int(most_frequent_no))
            else:     
                score = f1_score(y_true, y_pred, average='micro')        
            scores.append(score)
            weights.append(weight)
            
            print '---------'
            print y_true
            print y_pred
            print 'Target word: %s ; F1 = %f' % (target_word, score)
            
        print 'Average unweighted score %f' % (numpy.average (scores))
        print 'Average weighted score %f' % (numpy.average (scores, weights=weights))
    
    def baseline_pattern(self):
        scores = []
        weights = []
        for target_word in self.pattern_data[TEST]:
            y_true = []
            y_pred = []
            weight = 0
            print target_word
            most_frequent_no = -1
            most_frequent = 0
            
            for pattern in self.pattern_data[TEST][target_word]:
                pattern_no, examples = (pattern[PATTERN_NUMBER], pattern[EXAMPLES])
                if len(examples) > most_frequent:
                    most_frequent = len(examples)
                    most_frequent_no = pattern_no
                weight += len(examples)
                    
            for pattern in self.pattern_data[TEST][target_word]:
                pattern_no, examples = (pattern[PATTERN_NUMBER], pattern[EXAMPLES])
                for _ in examples:
                    y_true.append(int(pattern_no))
                    y_pred.append(int(most_frequent_no))
            
            if len(set(y_true)) == 2:
                score = f1_score(y_true, y_pred, average='weighted', pos_label=int(most_frequent_no))
            else:     
                score = f1_score(y_true, y_pred, average='weighted')
            scores.append(score)
            weights.append(weight)
            
            print y_true
            print y_pred
            print 'Target word: %s ; F1 = %f' % (target_word, score)
        
        print 'Average unweighted score %f' % (numpy.average (scores))
        print 'Average weighted score %f' % (numpy.average (scores, weights=weights))
    
    def read_pattern(self):
        with open(self.pattern_sample_file, "r") as filehandler:
            self.pattern_data = json.load(filehandler)
                        
    def create_pattern_prototypes(self):
        print 'Create pattern prototypes'
        self.prototypes = {}
        
        counter = 0
        for target_word in self.pattern_data[TRAIN]:
            counter += 1
            print 'Create prototype for %s' % target_word
            self.prototypes[target_word] = {}
            for pattern in self.pattern_data[TRAIN][target_word]:
                pattern_form, pattern_no, examples = (pattern[PATTERN],
                            pattern[PATTERN_NUMBER], pattern[EXAMPLES])
                
                average_vector = numpy.zeros(self.dim)
                
                p = pattern_form
                for removing_str in REMOVING_STRS:
                    p = p.replace(removing_str, ' ')
                p = p.lower()
                
                '''Give 1/5 of all example weight to pattern'''
                average_vector += float(len(examples))/5 * self._process_sentence(target_word + 's', p)
                
                for example in examples:
                    sentence = ' '.join([example[LEFT], example[TARGET], example[RIGHT]])
                    average_vector += self._process_sentence(example[TARGET], sentence)
                
                norm = numpy.linalg.norm(average_vector)
                if norm != 0:
                    average_vector = average_vector/ norm
                    self.prototypes[target_word][pattern_no] = average_vector
#             print self.prototypes[target_word]
    
    def save_prototypes(self, file_name):
        prototype_copy = {}
        for target_word in self.prototypes:
            prototype_copy[target_word] = {}
            for pattern_no in self.prototypes[target_word]:
                prototype_copy[target_word][pattern_no] = list(self.prototypes[target_word][pattern_no])
                
        with codecs.open(file_name, 'w', 'utf-8') as file_handler:
            json.dump(prototype_copy, file_handler)
            
    def load_prototypes(self, file_name):
        with codecs.open(file_name, 'r', 'utf-8') as file_handler:
            prototype_copy = json.load(file_handler)
        
        for target_word in prototype_copy:
            if target_word not in self.prototypes:
                self.prototypes[target_word] = {}
            for pattern_no in prototype_copy[target_word]:
                self.prototypes[target_word][pattern_no] = numpy.array(prototype_copy[target_word][pattern_no])
                self.prototypes[target_word][pattern_no]/=  numpy.linalg.norm(self.prototypes[target_word][pattern_no])
        
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
                average_vector += self.vector_data[word]
                
        return average_vector/ numpy.linalg.norm(average_vector)
    
    def read_vector_file(self):
        if self.vector_binary:
            self._read_raw_file()
        else:
            self._read_text_file()
    
    def _read_text_file(self):
        self.vector_data = {}
        with open(self.vector_file, "r") as filehandler:
            first_line = True
            for line in filehandler:
                values = line.split()
                if first_line:
                    self.words = int(values[0])
                    self.dim = int(values[1])
                    first_line = not first_line
                else:
                    word = values[0]
                    t = numpy.array(values)
                    self.vector_data[word] = t / numpy.linalg.norm(t)
                
        
    def _read_raw_file(self):
        self.vector_data = {}
        with open(self.vector_file, "rb") as filehandler:
            tempo = ''
            char = filehandler.read(1)
            while ord(char) != 32:
                tempo += char
                char = filehandler.read(1)
            self.words = int(tempo)
            
            tempo = ''
            char = filehandler.read(1)
            while ord(char) != 10:
                tempo += char
                char = filehandler.read(1)
            self.dim = int(tempo)
            
            print 'Number of words is %s' % self.words
            print 'Dimension of vectors is %s' % self.dim
            
            counter = 0
            for _ in xrange(200000):
#             for _ in xrange(self.words):
                tempo = ''
                while True:
                    char = filehandler.read(1)
                    if char == None or ord(char) == 32 or ord(char) == 10:
                        break
                    else:
                        tempo += char
                word = tempo
                
                if counter == 0:
                    sys.stdout.write('Process %s words' % counter)
                    
                if counter % 10000 == 0:
                    sys.stdout.write('\rProcess %s words' % counter)
                counter += 1
                
                vector = [0] * self.dim
                for a in xrange(self.dim):
                    vector[a] = struct.unpack("f", filehandler.read(4))[0]
                
                t = numpy.array(vector)
                self.vector_data[word] = t/ numpy.linalg.norm(t)
                
# def get_f1_score(y_true, y_pred, no_of_labels, labels=None, pos_label=1, average='weighted',
#              sample_weight=None):
#     if not no_of_labels == 2:
#         return f1_score(y_true, y_pred, labels, pos_label, average, sample_weight)
#     else:
#         f1_score(y_true, y_pred, labels, pos_label, average, sample_weight)
    
if __name__ == '__main__':
    '''
    [1, 1, 2, 2, 2]
    [2, 2, 2, 2, 2]
    
    [0, 0, 1, 1, 1]
    [1, 1, 1, 1, 1]
    
    [2, 2, 2, 2, 2, 3, 3]
    [2, 2, 2, 2, 2, 2, 2]
    '''
#     print precision_score([0, 0, 1, 1], [1, 1, 1, 1])
#     print recall_score([0, 0, 1, 1], [1, 1, 1, 1])
#     print f1_score([0, 0, 1, 1, 1], [1, 1, 1, 1, 1], average='weighted')
    
#     print precision_score([0, 0, 1, 1], [0, 0, 0, 0], average = 'weighted')
    
#     print confusion_matrix([0, 0, 1, 1], [1, 1, 1, 0])
#     print precision_score([0, 0, 1, 1], [1, 1, 1, 0], average = 'micro', pos_label=0)
#     print precision_score([0, 0, 1, 1], [1, 1, 1, 0], average = 'macro', pos_label=0)
#     print precision_score([0, 0, 1, 1], [1, 1, 1, 0], average = 'weighted', pos_label=0)
#     print recall_score([0, 0, 1, 1], [1, 1, 1, 0], average = 'micro', pos_label=0)
#     print recall_score([0, 0, 1, 1], [1, 1, 1, 0], average = 'macro', pos_label=0)
#     print recall_score([0, 0, 1, 1], [1, 1, 1, 0], average = 'weighted', pos_label=0)
#     print '-------'
#     print confusion_matrix([0, 0, 1, 1], [1, 0, 0, 0])
#     print precision_score([0, 0, 1, 1], [1, 0, 0, 0], average = 'micro')
#     print precision_score([0, 0, 1, 1], [1, 0, 0, 0], average = 'macro')
#     print precision_score([0, 0, 1, 1], [1, 0, 0, 0], average = 'weighted')
#     print recall_score([0, 0, 1, 1], [1, 0, 0, 0], average = 'micro')
#     print recall_score([0, 0, 1, 1], [1, 0, 0, 0], average = 'macro')
#     print recall_score([0, 0, 1, 1], [1, 0, 0, 0], average = 'weighted')
#     print '-------'
#     print precision_score([1, 1, 1, 1], [1, 2, 3, 4], average = 'micro')
#     print precision_score([1, 1, 1, 1], [1, 2, 3, 4], average = 'macro')
#     print precision_score([1, 1, 1, 1], [1, 2, 3, 4], average = 'weighted')
#     print recall_score([1, 1, 1, 1], [1, 2, 3, 4], average = 'micro')
#     print recall_score([1, 1, 1, 1], [1, 2, 3, 4], average = 'macro')
#     print recall_score([1, 1, 1, 1], [1, 2, 3, 4], average = 'weighted')
#     print '-------'
#     print precision_score([1, 2, 3, 4], [1, 1, 1, 1], average = 'micro')
#     print precision_score([1, 2, 3, 4], [1, 1, 1, 1], average = 'macro')
#     print precision_score([1, 2, 3, 4], [1, 1, 1, 1], average = 'weighted')
#     print recall_score([1, 2, 3, 4], [1, 1, 1, 1], average = 'micro')
#     print recall_score([1, 2, 3, 4], [1, 1, 1, 1], average = 'macro')
#     print recall_score([1, 2, 3, 4], [1, 1, 1, 1], average = 'weighted')
#     print f1_score([0, 0, 1, 1, 2], [0, 0, 0, 0, 0], average='weighted')
    t = Seed_Vector(WORD2VEC_POS_FRE, PATTERN_SPLIT_FILE, 5, True)
    t.read_pattern()
#     t.baseline_pattern()
    
    t.read_vector_file()
    t.create_pattern_prototypes()
#     t.test_pattern_prototypes()