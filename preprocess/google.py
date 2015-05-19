'''
Created on Mar 5, 2015

@author: Tuan Do
'''
import codecs
import json
import struct

import numpy

from utils import GOOGLE_DATA_FILE, VERBS, TYPEDM_VERB_VECTOR_FILE, GOOGLE_VERB_VECTOR_FILE, \
    GOOGLE_ADJECTIVE_VECTOR_FILE, ADJECTIVES, GOOGLE_ADVERB_VECTOR_FILE, ADVERBS, \
    NOUNS, GOOGLE_NOUN_VECTOR_FILE, ARTICLES, GOOGLE_ARTICLE_VECTOR_FILE, \
    CONJUNCS, GOOGLE_CONJUNC_VECTOR_FILE, LENCI_NOUNS, \
    LENCI_HYPONYMS, LENCI_HYPERNYMS, LENCI_WORD_RANKS, GOOGLE_DATA_300K
from cluster.word_cluster import verb_adj_simi_separator
from plurality import get_plural_form


class GoogleData(object):
    '''
    classdocs
    '''


    def __init__(self, data_file):
        '''
        Constructor
        '''
        self.data_file = data_file
    
    @staticmethod    
    def keep_word_in_file(word_file):
        word_dict = dict()
        with codecs.open(word_file, 'r', 'UTF-8') as filehandler:
            for line in filehandler:
                word = str(line.strip())
                word_dict[word] = 1
                
        def word_in_file(word):
            return word in word_dict
        
        word_in_file.length = len(word_dict.keys())
        return word_in_file
    
    @staticmethod
    def is_single_word(word):
        if word.find('_') == -1:
            return True
        return False
    
    def filter(self, function, keep_word_dict):
        print 'Begin filtering'
        self.word_vector = dict()
        self.word_list = []
        
        with open(self.data_file, "rb") as filehandler:
            tempo = ''
            char = filehandler.read(1)
            while ord(char) != 32:
                tempo += char
                char = filehandler.read(1)
            self.words = int(tempo)
#              
            tempo = ''
            char = filehandler.read(1)
            while ord(char) != 10:
                tempo += char
                char = filehandler.read(1)
            self.dim = int(tempo)
            
            print self.words
            print self.dim
            
            counter = 0
#             for _ in xrange(self.words):
            for _ in xrange(300000):
                tempo = ''
                while True:
                    char = filehandler.read(1)
                    if char == None or ord(char) == 32 or ord(char) == 10:
                        break
                    else:
                        tempo += char
                word = tempo
                
#                 if not function(word) and word not in keep_word_dict:
#                     filehandler.seek(4 * self.dim, 1)
#                     continue
#                 
#                 if counter > 5000 and word not in keep_word_dict:
#                     filehandler.seek(4 * self.dim, 1)
#                     continue
                
                if counter % 100 == 0:
                    print counter
                counter += 1
                
                vector = [0] * self.dim
                for a in xrange(self.dim):
                    vector[a] = struct.unpack("f", filehandler.read(4))[0]
                
                leng = 0
                for a in xrange(self.dim):
                    leng += vector[a] * vector[a]
                leng = numpy.sqrt(leng)
                vector = [v / leng for v in vector]
                self.word_list.append(word)
                self.word_vector[word] = vector
                
#                 if counter == function.length:
#                     break
    
    @staticmethod
    def read_raw_file(raw_file):
        vector_data = {}
        with open(raw_file, "rb") as filehandler:
            tempo = ''
            char = filehandler.read(1)
            while ord(char) != 32:
                tempo += char
                char = filehandler.read(1)
            words = int(tempo)
            
            tempo = ''
            char = filehandler.read(1)
            while ord(char) != 10:
                tempo += char
                char = filehandler.read(1)
            dim = int(tempo)
            
            print words
            print dim
            
            counter = 0
#             for _ in xrange(words):
            for _ in xrange(200000):
                tempo = ''
                while True:
                    char = filehandler.read(1)
                    if char == None or ord(char) == 32 or ord(char) == 10:
                        break
                    else:
                        tempo += char
                word = tempo
                
                if counter % 1000 == 0:
                    print counter
                counter += 1
                
                vector = [0] * dim
                for a in xrange(dim):
                    vector[a] = struct.unpack("f", filehandler.read(4))[0]
                vector = numpy.array(vector)
                vector = vector/numpy.sqrt(vector.dot(vector))
                vector_data[word] = vector
        
        return vector_data
    
    def produce_words (self, file_names):
        word_dict = dict()
        for file_name in file_names:
            with codecs.open(file_name, 'r', 'UTF-8') as filehandler:
                for line in filehandler:
                    word = str(line.strip())
                    word_dict[word] = 1
                    word_dict[get_plural_form(word)] = 1
        
        return word_dict
    
    def produce_ranks(self, word_dict, output_file_name):
        print 'Begin finding ranks'
        self.word_ranks = dict()
        
        with open(self.data_file, "rb") as filehandler:
#             self.no_of_words = struct.unpack("ll",filehandler.read(8))
#             self.dim = struct.unpack("ll",filehandler.read(8))
            
            tempo = ''
            char = filehandler.read(1)
            while ord(char) != 32:
                tempo += char
                char = filehandler.read(1)
            self.words = int(tempo)
#              
            tempo = ''
            char = filehandler.read(1)
            while ord(char) != 10:
                tempo += char
                char = filehandler.read(1)
            self.dim = int(tempo)
            
            print self.words
            print self.dim
            
            counter = 0
            for i in xrange(self.words):
#             for i in xrange(1000):
                tempo = ''
                while True:
                    char = filehandler.read(1)
                    if char == None or ord(char) == 32 or ord(char) == 10:
                        break
                    else:
                        tempo += char
                word = tempo.strip()
#                 print word
                if word not in word_dict:
                    filehandler.seek(4 * self.dim, 1)
                    continue
                 
                print word + " " + str(i)
                 
                counter += 1
                 
                self.word_ranks[word] = i
                
                filehandler.seek(4 * self.dim, 1)
                
        with codecs.open(output_file_name, 'w', 'UTF-8') as filehandler:
            json.dump(self.word_ranks, filehandler)
                
    def save_to_file(self, vector_file):
        print 'Begin save to json file ' + vector_file
        with codecs.open(vector_file, 'w', 'UTF-8') as filehandler:
            json.dump(self.word_vector, filehandler) 
    
    def save_to_binary_file(self, binary_file):
        print 'Begin save to binary file ' + binary_file
        with open(binary_file, "wb") as filehandler:
            words = len(self.word_vector.keys())
            dim = len(self.word_vector[self.word_vector.keys()[0]])
            for c in str(words):
                filehandler.write(c)
            filehandler.write(' ')
            for c in str(dim):
                filehandler.write(c)
            filehandler.write('\n')
            
            for word in self.word_list:
                vector = self.word_vector[word]
                for c in word:
                    filehandler.write(c)
                filehandler.write(' ')
                
                s = struct.pack('f' * len(vector), *vector)
                filehandler.write(s)
    
if __name__ == '__main__':
    google = GoogleData(GOOGLE_DATA_FILE)
    
#     google.word_vector = {'I':[2,3], 'am':[3,4]}
#     google.save_to_binary_file('verb.bin')
    
    google.filter(GoogleData.is_single_word, [])
    google.save_to_binary_file(GOOGLE_DATA_300K)
    
#     print GoogleData.is_single_word('Chinese')

#     google.filter(GoogleData.keep_word_in_file(VERBS))
#     google.save_to_file(GOOGLE_VERB_VECTOR_FILE)
    
#     word_dict = dict()
#     with codecs.open(LENCI_NOUNS, 'r', 'UTF-8') as filehandler:
#         for line in filehandler:
#             word = str(line.strip())
#             word_dict[word] = 1
#                 
#     google.filter(GoogleData.keep_word_in_file(NOUNS), word_dict)
#     google.save_to_file(GOOGLE_NOUN_VECTOR_FILE)
#     print google.produce_words([LENCI_HYPONYMS, LENCI_HYPERNYMS])
#     google.produce_ranks(google.produce_words([LENCI_HYPONYMS, LENCI_HYPERNYMS]), LENCI_WORD_RANKS)

#     google.filter(GoogleData.keep_word_in_file(ADJECTIVES))
#     google.save_to_file(GOOGLE_ADJECTIVE_VECTOR_FILE)
    
#     google.filter(GoogleData.keep_word_in_file(ADVERBS))
#     google.save_to_file(GOOGLE_ADVERB_VECTOR_FILE)
    
#     google.filter(GoogleData.keep_word_in_file(NOUNS))
#     google.save_to_file(GOOGLE_NOUN_VECTOR_FILE)

#     google.filter(GoogleData.keep_word_in_file(ARTICLES))
#     google.save_to_file(GOOGLE_ARTICLE_VECTOR_FILE)
