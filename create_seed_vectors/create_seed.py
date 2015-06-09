'''
Created on May 12, 2015

@author: Tuan Do
'''
from _collections import defaultdict
import codecs
import json
import os
import re
import struct
import sys

from gensim import utils
import gensim
from numpy import uint32, random
import numpy
from sklearn.metrics import f1_score, precision_score, recall_score, confusion_matrix
from spacy.en import English

from bnc.util import process_sentence
from create_seed_vectors import REMOVING_STRS, TRAIN, TEST, WORD2VEC_POS, \
    SEED_VECTOR_FILE, WORD2VEC_VOCAB, \
    PATTERN_SPLIT_FILE_EXTEND


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
FULL_EXAMPLE = 'full_examples'
PERCENTAGE = 'per'
REF = 'ref'
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

DEBUG_MODE = False
DEBUG_VERBS = ['allocate'] 

def clear_digits(s):
    return re.sub('\\$?-?[0-9]+(\\,[0-9]+)*(\\.[0-9]+)*', 'number', s)
    
def parse_sentence(sentence):
    result = []
    sentence = process_sentence(clear_digits(sentence))
    pos_results = nlp(sentence)
    for token_struct in pos_results:
        token, pos = token_struct.orth_, token_struct.tag_
        pos = get_brief_pos(pos)
        token = token.lower()
        result.append(token + '-' + pos)
    return result

def get_brief_pos(old_pos):
    pos = old_pos.lower()
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
    return pos

def f_score_two_labels(y_true, y_pred, average='weighted'):
    '''
    average = 'micro'
            = 'macro'
            = 'weighted'
    Calculate for two labels in the same manner as multiple labels
    '''
    if average == 'micro':
        count = 0
        for i in xrange(len(y_true)):
            if y_true[i] == y_pred[i]:
                count += 1
        return float(count) / len(y_true)
    if average == 'macro':
        labels = set(y_true)
        t_score = 0
        for label in labels:
            t_score += f1_score(y_true, y_pred, pos_label=int(label))
        t_score /= len(labels)
        return t_score
    if average == 'weighted':
        labels = set(y_true)
        label_count = defaultdict(int)
        t_score = 0
        for i in xrange(len(y_true)):
            label_count[y_true[i]] += 1
        for label in labels:
            t_score += label_count[label] * f1_score(y_true, y_pred, pos_label=int(label))
        t_score /= len(y_true)
        return t_score
    
    
class Seed_Vector(object):
    '''
    classdocs
    '''

    def __init__(self, vector_file, pattern_sample_file, window_size, vector_binary=True, margin=1.0):
        '''
        two_component_vector_file:
        A file in the same format as word2vec vector
        
        pattern_sample_file:
        '''
        self.vector_file = vector_file
        self.pattern_sample_file = pattern_sample_file
        self.window_size = window_size
        self.vector_binary = vector_binary
        self.margin = margin
        self.read_vocab()
        
    def read_vocab(self):
        counter = 0
        self.vocab = {}
        with codecs.open(WORD2VEC_VOCAB, "r", 'utf-8') as filehandler:
            for line in filehandler:
                counter += 1
                if counter > 100:
                    word, freq = line.strip().split()
                    self.vocab[word] = freq
        
    
    def test_pattern_prototypes(self, average='weighted', retest = False):
        print 'Test pattern prototypes'
        scores = []
        weights = []
        
        counter = 0
        
        if DEBUG_MODE:
            target_words = DEBUG_VERBS
        else:
            target_words = self.pattern_data[TRAIN]
            
        if retest:
            data_set = TRAIN
        else:
            data_set = TEST
            
        for target_word in target_words:
#             if counter > 3:
#                 break
            counter += 1
            y_true = []
            y_pred = []
            weight = 0
            
            most_frequent_no = -1
            most_frequent = 0
            
            for pattern in self.pattern_data[data_set][target_word]:
                pattern_no, examples = (pattern[PATTERN_NUMBER], pattern[EXAMPLES])
                if len(examples) > most_frequent:
                    most_frequent = len(examples)
                    most_frequent_no = pattern_no
                weight += len(examples)
                
            for pattern in self.pattern_data[data_set][target_word]:
                pattern_no, examples = (pattern[PATTERN_NUMBER], pattern[EXAMPLES])
                
                for example_index, example in enumerate(examples):
                    key = '%s_%s_%s' % (target_word, pattern_no, example_index)
                    average_vector = self._get_average_vector_from(example, TEST, key, self.window_size)
                    values = [(p, average_vector.dot(self.normalized_prototypes[target_word][p])) for p in self.prototypes[target_word].keys()]
                    values = sorted(values, key=lambda x : x[1])
                    best = values[-1][0]
                    
                    best_value = values[-1][1]
                    second_best_value = values[-2][1]
                    
                    if 'margin' not in self.__dict__:
                        self.margin = 1.0
                    
                    if best_value != 0:
                        y_true.append(int(pattern_no))
                        y_pred.append(int(best))
#                     if second_best_value == 0 or best_value / second_best_value > self.margin:
#                         y_true.append(int(pattern_no))
#                         y_pred.append(int(best))
#                         
                    elif best_value == 0:
                        average_vector = self._get_average_vector_from(example, TEST, key, 2 * self.window_size)
                        values = [(p, average_vector.dot(self.normalized_prototypes[target_word][p])) for p in self.prototypes[target_word].keys()]
                        values = sorted(values, key=lambda x : x[1])
                        best = values[-1][0]
                        y_true.append(int(pattern_no))
                        y_pred.append(int(best))
                    
                    if DEBUG_MODE:
                        print '-- Example is of pattern %s, classified as %s' % (pattern_no, best)
                            
                weight += len(examples)
            
            score = None
            if len(set(y_true)) == 2 and most_frequent_no in set(y_true):
                score = f_score_two_labels(y_true, y_pred, average=average)
            elif len(set(y_true)) > 2:     
                score = f1_score(y_true, y_pred, average=average)
            
            if score != None:        
                scores.append(score)
                weights.append(weight)
                
                print '---------'
                print ','.join(['%3d' % t for t in y_true])
                print ','.join(['%3d' % t for t in y_pred])
                print 'Target word: %s ; F1 = %f' % (target_word, score)
                
                labels = sorted(list(set(y_true).union(set(y_pred))))
                print 'Labels  %s' % labels
                t = numpy.array(confusion_matrix(y_true, y_pred, labels), dtype=float)
                print 'Confusion matrix '
                print t
                '''Normalize by row'''
                t_row = (t.transpose() / numpy.sum(t, axis=1)).transpose()
                print t_row

                
                di = numpy.diag_indices(len(labels))
                t_row[di] = 0
                t[di] = 0

                raw_max = numpy.unravel_index(numpy.argmax(t), (len(labels), len(labels)))
                row_max = numpy.unravel_index(numpy.argmax(t_row), (len(labels), len(labels)))

                print 'Most confused based on unnormalized; between pattern %s and pattern %s' % (labels[raw_max[0]], labels[raw_max[1]])
                print 'Most confused based on row; between pattern %s and pattern %s' % (labels[row_max[0]], labels[row_max[1]])
#                 '''Normalize by column'''
#                 t_col = t / numpy.sum(t, axis = 0)
#                 print t_col
#                 t_col[di] = 0
#                 col_max = numpy.unravel_index(numpy.argmax(t_col),  (len(labels), len(labels)) )
#                 print 'Most confused based on col; between pattern %s and pattern %s' % (labels[col_max[0]], labels[col_max[1]])

        print 'Average unweighted score %f' % (numpy.average (scores))
        print 'Average weighted score %f' % (numpy.average (scores, weights=weights))
        
    def _get_average_vector_from(self, example, data_type, key, window_size):
        sentence = ' '.join([example[LEFT], example[TARGET], example[RIGHT]])
        return self._process_sentence(example[TARGET], sentence, window_size)
    
    def baseline_pattern(self, average='weighted'):
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
                score = f_score_two_labels(y_true, y_pred, average=average)
            else:     
                score = f1_score(y_true, y_pred, average=average)
            scores.append(score)
            weights.append(weight)
            
            print y_true
            print y_pred
            print 'Target word: %s ; F1 = %f' % (target_word, score)
        
        print 'Average unweighted score %f' % (numpy.average (scores))
        print 'Average weighted score %f' % (numpy.average (scores, weights=weights))
    
    def generate_random_prototypes(self):
        '''
        Generate random vectors
        Run only after load the original vectors model
        '''
        print 'Create random prototypes'
        word_list = self.vector_data.keys()
        for word in word_list:
            # construct deterministic seed from word AND seed argument
            # Note: Python's built in hash function can vary across versions of Python
            random.seed(uint32(hash(word + str(1))))
            self.vector_data[word] = (random.rand(self.dim) - 0.5) / self.dim
        self.create_pattern_prototypes()
        
    def read_pattern(self):
        print 'Read pattern file'
        with open(self.pattern_sample_file, "r") as filehandler:
            self.pattern_data = json.load(filehandler)
                        
    def create_pattern_prototypes(self):
        print 'Create pattern prototypes'
        self.prototypes = {}
        self.normalized_prototypes = {}
        
        counter = 0
        if DEBUG_MODE:
            target_words = DEBUG_VERBS
        else:
            target_words = self.pattern_data[TRAIN]
            
        for target_word in target_words:
            counter += 1
            print 'Create prototype for %s' % target_word
            self.prototypes[target_word] = {}
            self.normalized_prototypes[target_word] = {}
            
            for pattern in self.pattern_data[TRAIN][target_word]:
                pattern_form, pattern_no, examples = (pattern[PATTERN],
                            pattern[PATTERN_NUMBER], pattern[EXAMPLES])
                if DEBUG_MODE:
                    print '=== Create prototype for pattern %s' % pattern_no
                
                average_vector = numpy.zeros(self.dim)
                
                p = pattern_form
                for removing_str in REMOVING_STRS:
                    p = p.replace(removing_str, ' ')
                p = p.lower()
                
                '''Give 1/5 of all example weight to pattern'''
                average_vector += float(len(examples)) / 5 * self._process_sentence(target_word + 's', p, self.window_size)
                
                for example_index, example in enumerate(examples):
                    key = '%s_%s_%s' % (target_word, pattern_no, example_index)
                    v = self._get_average_vector_from(example, TRAIN, key, self.window_size)
                    average_vector += v
                
                '''Unnormalized prototype'''
                self.prototypes[target_word][pattern_no] = average_vector
                
                norm = numpy.linalg.norm(average_vector)
                if norm != 0:
                    self.normalized_prototypes[target_word][pattern_no] = average_vector / norm
                
                if DEBUG_MODE:
                    print 'Prototype %s' % pattern_no
                    print self.normalized_prototypes[target_word][pattern_no][:10]
                    
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
                self.normalized_prototypes[target_word] = {}
                
            for pattern_no in prototype_copy[target_word]:
                self.prototypes[target_word][pattern_no] = numpy.array(prototype_copy[target_word][pattern_no])
                self.normalized_prototypes[target_word][pattern_no] = self.prototypes[target_word][pattern_no] / numpy.linalg.norm(self.prototypes[target_word][pattern_no])
        
    def _process_sentence(self, target_word, sentence, window_size):
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
        
        for index, token_w_pos in enumerate(parsed):    
            if token_w_pos == target_word + '-n' or token_w_pos == target_word + '-j':
                target_index = index
                break
            
        average_vector = numpy.zeros(self.dim)
        if target_index == -1:
            return average_vector
        
        for index in xrange(target_index - window_size, target_index + window_size + 1):
            if index < 0 or index >= len(parsed):
                continue
            word = parsed[index]
            
            if word in self.vector_data:
                average_vector += self.vector_data[word]
                
        if DEBUG_MODE:
            print sentence
            print [parsed[index] for index in xrange(target_index - window_size,\
                                                      target_index + window_size + 1) if index >= 0 and index < len(parsed) and parsed[index] in self.vector_data]
                
        return average_vector / numpy.linalg.norm(average_vector)
    
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
        print 'Read raw file'
        self.vector_data = {}
        model = gensim.models.Word2Vec.load_word2vec_format(self.vector_file, binary=True)
        vectors = model.syn0
        self.dim = model.layer1_size
        self.words = len(model.index2word)
        for i in xrange(self.words):
            self.vector_data[model.index2word[i]] = vectors[i]
        
    def _read_raw_file_old(self):
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
#             for _ in xrange(200000):
            for _ in xrange(self.words):
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
                self.vector_data[word] = t / numpy.linalg.norm(t)
                
if __name__ == '__main__':
#     print clear_digits('Def 147,234.234 Abc')
#     print clear_digits('d a $175 million plan to plant 1,000 million trees')

#     t = Seed_Vector(WORD2VEC_POS, PATTERN_SPLIT_FILE, 5, True)
#     t.read_vector_file()
#     y_true = [0,0,1,1,1]
#     y_pred = [0,1,1,1,1]
#     print f1_score(y_true, y_pred, average='micro', pos_label=int(1))
#     print f1_score(y_true, y_pred, average='macro', pos_label=int(1))
#     print f1_score(y_true, y_pred, average='weighted', pos_label=int(1))
#      
#     print f1_score(y_true, y_pred, average='micro', pos_label=int(0))
#     print f1_score(y_true, y_pred, average='macro', pos_label=int(0))
#     print f1_score(y_true, y_pred, average='weighted', pos_label=int(0))
#     
#     print f_score_two_labels(y_true, y_pred, average='micro')
#     print f_score_two_labels(y_true, y_pred, average='macro')
#     print f_score_two_labels(y_true, y_pred, average='weighted')
#     
#     y_true = [0,0,0,1,2]
#     y_pred = [0,1,1,2,2]
#     print f1_score(y_true, y_pred, average='micro')
#     print f1_score(y_true, y_pred, average='macro')
#     print f1_score(y_true, y_pred, average='weighted')
 
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
     
#     t.print_train_statistics()
#     t.print_test_statistics()
     
# #     t.save_prototypes(PROTOTYPE_POS)
# #     t.load_prototypes(PROTOTYPE_POS_AFTER_RETRAIN)
    for method in ['micro', 'macro', 'weighted']:
        print '===================================================================='
        print 'Test SG-NS F1 for %s' % method
        t.test_pattern_prototypes(average=method)
        print '===================================================================='
 
#     for pattern in t.pattern_data[TRAIN]['call']:
#         no, examples, p = (pattern[PATTERN_NUMBER], pattern[EXAMPLES], pattern[PATTERN])
#         print '%s %s' % (no , p)
