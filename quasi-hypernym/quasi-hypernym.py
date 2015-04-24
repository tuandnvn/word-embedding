'''
Created on Apr 14, 2015

@author: Tuan Do
'''
from utils import GOOGLE_ADJECTIVE_VECTOR_FILE, SCALE_ADJ, GOOGLE_DATA_300K,\
    ORDERED_SCALE_ADJ
import codecs
import json
from preprocess.calculate_neighbors import CalculateNeighbors
import numpy
import struct
from preprocess.google import GoogleData

class QuasiHypernym():
    def __init__(self, vector_file = None, raw_file = None):
        '''
        Constructor
        '''
        self.vector_data = {}
        if vector_file != None:
            self.vector_file = vector_file
            
            with codecs.open(vector_file, 'r', 'UTF-8') as filehandler:
                self.vector_data = json.load(filehandler)
            
            print 'Finish loading vector file'
        if raw_file != None:
            self.raw_file = raw_file
            self.vector_data = GoogleData.read_raw_file(self.raw_file)
            
            print 'Finish loading raw file'
    
    def calculate_distance(self, list_of_words):
        distances = []
        
        normalized = {}
        for word in list_of_words:
            if word in self.vector_data:
                t = numpy.array(self.vector_data[word])
                normalized[word] = t / numpy.sqrt(t.dot(t)) 
            
        for index_1, word_1 in enumerate(normalized.keys()):
            for index_2, word_2 in enumerate(normalized.keys()):
                if index_1 < index_2:
                    distances.append((word_1, word_2,\
                         CalculateNeighbors.dot_similarity(normalized[word_1], normalized[word_2])))
        return sorted(distances, key=lambda x : -x[2])
    
    def triple_calculate(self, list_of_word_pairs, alpha = 0.5):
        triples = []
        correct_number = 0
        correct_number_2 = 0
        
        for word_1, word_2 in list_of_word_pairs:
            for word_3, word_4 in list_of_word_pairs:
                if word_2 == word_3:
                    if word_1 in self.vector_data and \
                        word_2 in self.vector_data and \
                        word_4 in self.vector_data:
                        triples.append((word_1, word_2, word_4))
            
                        similarity_1_2 = CalculateNeighbors.dot_similarity(self.vector_data[word_1], self.vector_data[word_2])
                        similarity_2_3 = CalculateNeighbors.dot_similarity(self.vector_data[word_2], self.vector_data[word_4])
                        similarity_1_3 = CalculateNeighbors.dot_similarity(self.vector_data[word_1], self.vector_data[word_4])
                        
                        print (word_1, word_2, word_4)
                        print str(similarity_1_2) + ' ' + str(similarity_2_3) + ' ' + str(similarity_1_3)
                        if  similarity_1_2 > similarity_1_3 and similarity_2_3 > similarity_1_3:
                            correct_number += 1
                            
                            if numpy.arccos(similarity_1_2) + numpy.arccos(similarity_2_3) < (1 + alpha) * numpy.arccos(similarity_1_3):
                                correct_number_2 += 1
        
        print correct_number
        print correct_number_2
        print len(triples)
        
if __name__ == '__main__':
    t = QuasiHypernym(raw_file = GOOGLE_DATA_300K)
    
    def scale_adj():
        words = {}
        with codecs.open(SCALE_ADJ, 'r', 'UTF-8') as filehandler:
            list_of_words = None
            for line in filehandler:
                if line[:1] == ':':
                    if list_of_words != None:
                        words[semantic_type] = list_of_words
                    semantic_type = line.strip().split()[1]
                    list_of_words = []
                else:
                    list_of_words.append(line.strip())
            words[semantic_type] = list_of_words    
        
        for semantic_type in words:
            print t.calculate_distance(words[semantic_type])
    
    def triple_adj():
        words = {}
        with codecs.open(ORDERED_SCALE_ADJ, 'r', 'UTF-8') as filehandler:
            list_of_word_pairs = None
            for line in filehandler:
                if line[:1] == ':':
                    if list_of_word_pairs != None:
                        words[semantic_type] = list_of_word_pairs
                    semantic_type = line.strip().split()[1]
                    list_of_word_pairs = []
                else:
                    list_of_word_pairs.append(line.strip().split())
            words[semantic_type] = list_of_word_pairs
        
        for semantic_type in words:
            print semantic_type
            t.triple_calculate(words[semantic_type])
            
    triple_adj()