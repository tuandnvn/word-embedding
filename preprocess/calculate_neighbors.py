'''
Created on Feb 25, 2015

@author: Tuan Do
'''
import codecs
from copy import deepcopy
import heapq
import json
from multiprocessing import Manager
import multiprocessing
import threading

import numpy

from util import FRAMENET_SELECTED_FEATURES_VERB_VECTOR, \
    FRAMENET_VERB_VECTOR, VERB_SIMILAR_FRAMENET_ONLY, \
    VERB_SIMILAR_FRAMENET_ONLY_JSON, \
    VERB_SIMILAR_FRAMENET_ONLY_SELECTED_FEATURES, \
    VERB_SIMILAR_FRAMENET_ONLY_JSON_SELECTED_FEATURES, TYPEDM_VERB_VECTOR_FILE, TYPEDM_VERB_SIMILAR, \
    TYPEDM_VERB_SIMILAR_JSON, GOOGLE_VERB_VECTOR_FILE, GOOGLE_VERB_SIMILAR, \
    GOOGLE_VERB_SIMILAR_JSON, TYPEDM_VERB_VECTOR_FILE, GOOGLE_NOUN_VECTOR_FILE, \
    GOOGLE_NOUN_SIMILAR, GOOGLE_NOUN_SIMILAR_JSON


class Get_Similarity_Process(multiprocessing.Process):
    def __init__(self, begin, end, word_list_1, normalized_1, no_of_neighbors, similar_words):
        multiprocessing.Process.__init__(self)
        self.begin = begin
        self.end = end
        self.word_list_1 = deepcopy(word_list_1)
        self.normalized_1 = deepcopy(normalized_1)
        self.no_of_neighbors = no_of_neighbors
        self.similar_words = similar_words
    
    def run(self):
        for i in xrange(self.begin, self.end):
            if i % 10 == 0:
                print i
            word_1 = self.word_list_1[i]
            similarities = [CalculateNeighbors.dot_similarity(self.normalized_1[word_1], self.normalized_1[word_2])  for word_2 in self.word_list_1]
            nth_largest = heapq.nlargest(self.no_of_neighbors + 1, similarities)[-1]
            most_similar_indices = [index for index in xrange(len(similarities)) if similarities[index] >= nth_largest]
            self.similar_words[word_1] = [(self.word_list_1[index], similarities[index]) for index in most_similar_indices if self.word_list_1[index] != word_1]
            self.similar_words[word_1] = sorted(self.similar_words[word_1], key=lambda x : x[1])
            
class Save_To_Readable_Thread(multiprocessing.Process):
    def __init__(self, file_name, word_list_1, neighbor_number, similar_words, pos_type):
        multiprocessing.Process.__init__(self)
        self.file_name = file_name
        self.word_list_1 = word_list_1
        self.neighbor_number = neighbor_number
        self.similar_words = similar_words
        self.pos_type = pos_type
    
    def run(self):
        print 'save_to_readable_file ' + self.file_name
        with codecs.open(self.file_name, 'w', 'UTF-8') as filehandler:
            for word_1 in self.similar_words.keys():
                for word_2, similarity in self.similar_words[word_1][-self.neighbor_number:]:
                    filehandler.write(word_1)
                    filehandler.write('-' + self.pos_type + '\t')
                    filehandler.write(word_2)
                    filehandler.write('-' + self.pos_type + '\t')
                    filehandler.write(str(similarity))
                    filehandler.write('\n')
                    
class Save_To_JSON_Thread(multiprocessing.Process):
    def __init__(self, file_name, neighbor_number, similar_words):
        multiprocessing.Process.__init__(self)
        self.file_name = file_name
        self.neighbor_number = neighbor_number
        self.similar_words = similar_words
        
    def run(self):
        print 'save_to_json_file ' + self.file_name
        tempo = {}
        for word in self.similar_words.keys():
            tempo[word] = self.similar_words[word][-self.neighbor_number:]
        with codecs.open(self.file_name, 'w', 'UTF-8') as filehandler: 
            json.dump(tempo, filehandler)
                    
class CalculateNeighbors(object):
    '''
    classdocs
    '''


    def __init__(self, vector_file, pos_type='v'):
        '''
        Constructor
        '''
        self.vector_file = vector_file
        
        with codecs.open(vector_file, 'r', 'UTF-8') as filehandler:
            self.vector_data_1 = json.load(filehandler)
        
        self.pos_type = pos_type
        
#         if u'flirt' in self.vector_data_1:
#             print self.vector_data_1[u'elope']
    @staticmethod
    def dot_similarity(vector_1, vector_2):
        return vector_1 .dot(vector_2)
    
    @staticmethod
    def euclide_similarity(vector_1, vector_2):
        v = vector_1 - vector_2
        return -v.dot(v)
    
    @staticmethod
    def kl_similarity(vector_1, vector_2):
        v = vector_1.dot(numpy.log (vector_1 / vector_2)) + vector_2.dot(numpy.log (vector_2 / vector_1))
        return -v
    
    def find_k_nearest_neighbors(self, k):
        print 'find_k_nearest_neighbors ' + str(k)
        self.normalized_1 = dict()
        self.dim = 0
        self.k = k
        
        for word in self.vector_data_1:
            t = numpy.array(self.vector_data_1[word])
            self.normalized_1[word] = t / numpy.sqrt(t.dot(t)) 
            if self.dim == 0:
                self.dim = len(self.normalized_1[word])
        
        self.similar_words = dict()
        self.word_list_1 = [word for word in self.normalized_1]
        
        for i in xrange(len(self.word_list_1)):
            word_1 = self.word_list_1[i]
            similarities = [CalculateNeighbors.dot_similarity(self.normalized_1[word_1], self.normalized_1[word_2])  for word_2 in self.word_list_1]
            nth_largest = heapq.nlargest(k + 1, similarities)[-1]
            most_similar_indices = [index for index in xrange(len(similarities)) if similarities[index] >= nth_largest]
            self.similar_words[word_1] = [(self.word_list_1[index], similarities[index]) for index in most_similar_indices if self.word_list_1[index] != word_1]
            self.similar_words[word_1] = sorted(self.similar_words[word_1], key=lambda x : x[1])
    
    def find_k_nearest_neighbors_multi_thread(self, k, no_of_thread=8):
        print 'find_k_nearest_neighbors ' + str(k)
        self.normalized_1 = dict()
        self.dim = 0
        self.k = k
        
        for word in self.vector_data_1:
            t = numpy.array(self.vector_data_1[word])
            self.normalized_1[word] = t / numpy.sqrt(t.dot(t)) 
            if self.dim == 0:
                self.dim = len(self.normalized_1[word])
        
        manager = Manager()

        self.similar_words = manager.dict()
        self.word_list_1 = [word for word in self.normalized_1]
        
        print len(self.word_list_1)
            
        step = int(len(self.word_list_1) / (no_of_thread - 1))
        threads = []
        for i in xrange(no_of_thread):
            start = i * step
            end = numpy.min([(i + 1) * step, len(self.word_list_1)])
            print str(start) + " " + str(end)
            this_thread = Get_Similarity_Process(start, end, self.word_list_1, self.normalized_1, self.k, self.similar_words)
#             this_thread = multiprocessing.Process(target=calculate_for_range, args=(start, end,\
#                                             self.word_list_1, self.normalized_1, self.k, self.similar_words))
            threads.append(this_thread)
        
        print 'thread start'
        for this_thread in threads:
            this_thread.start()
            
        for this_thread in threads:
            this_thread.join()
            
        print 'thread has joined'
    
    def save_to_readable_file(self, word_similar_file, neighbor_numbers):
        """
        word_list_1 : array of string
        similar_words : dictionary [ string ] -> array of tuples ( string, similarity ) 
        """
        threads = []                    
        for neighbor_number in neighbor_numbers:
            if neighbor_number > self.k:
                continue
            file_name = word_similar_file.replace(".txt", "." + str(neighbor_number) + ".txt")
            this_thread = Save_To_Readable_Thread(file_name, self.word_list_1, \
                                                   neighbor_number, self.similar_words, self.pos_type)
            this_thread.start()
            threads.append(this_thread)
        
        for thread in threads:
            thread.join()
    
    def  save_to_json_file(self, word_similar_file, neighbor_numbers):
        threads = []                
        for neighbor_number in neighbor_numbers:
            if neighbor_number > self.k:
                continue
            file_name = word_similar_file.replace(".json", "." + str(neighbor_number) + ".json")
            this_thread = Save_To_JSON_Thread(file_name, neighbor_number, self.similar_words)
            this_thread.start()
            threads.append(this_thread)
        
        for thread in threads:
            thread.join()
            
if __name__ == '__main__':
    # t = CalculateNeighbors(FRAMENET_SELECTED_FEATURES_VERB_VECTOR, VERB_SIMILAR_SELECTED_FEATURES)
    # t = CalculateNeighbors(TYPEDM_VERB_VECTOR)
    # t.find_k_nearest_neighbors(100)
    # t.save_to_readable_file(TYPEDM_VERB_SIMILAR)
    # t.save_to_json_file(TYPEDM_VERB_SIMILAR_JSON)
    
#     t = CalculateNeighbors(FRAMENET_SELECTED_FEATURES_VERB_VECTOR)
#     t.find_k_nearest_neighbors(100)
#     t.save_to_readable_file(VERB_SIMILAR_FRAMENET_ONLY_SELECTED_FEATURES)
#     t.save_to_json_file(VERB_SIMILAR_FRAMENET_ONLY_JSON_SELECTED_FEATURES)
    
#     t = CalculateNeighbors(TYPEDM_VERB_VECTOR_FILE)
#     t.find_k_nearest_neighbors(100)
#     t.save_to_readable_file(TYPEDM_VERB_SIMILAR)
#     t.save_to_json_file(TYPEDM_VERB_SIMILAR_JSON)
    
#     number_of_neighbors = 200
#     neighbors = [25, 50, 100, 200]
#     
#     t = CalculateNeighbors(GOOGLE_VERB_VECTOR_FILE)
#     t.find_k_nearest_neighbors(number_of_neighbors)
#     t.save_to_readable_file(GOOGLE_VERB_SIMILAR, neighbors)
#     t.save_to_json_file(GOOGLE_VERB_SIMILAR_JSON, neighbors)
    
    number_of_neighbors = 200
    neighbors = [25, 50, 100, 200]
     
    t = CalculateNeighbors(GOOGLE_NOUN_VECTOR_FILE, pos_type='n')
#     t.find_k_nearest_neighbors(number_of_neighbors)
    t.find_k_nearest_neighbors_multi_thread(number_of_neighbors, no_of_thread=8)
    t.save_to_readable_file(GOOGLE_NOUN_SIMILAR, neighbors)
    t.save_to_json_file(GOOGLE_NOUN_SIMILAR_JSON, neighbors)
