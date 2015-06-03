'''
Created on Mar 10, 2015

@author: Tuan Do
'''
import codecs
import heapq
import json
from multiprocessing import Manager
import multiprocessing

import numpy

from util import GOOGLE_ADJECTIVE_VECTOR_FILE, GOOGLE_VERB_VECTOR_FILE, \
    GOOGLE_VERB_ADJECTIVE_SIMILAR, GOOGLE_VERB_ADJECTIVE_SIMILAR_JSON, \
    TYPEDM_VERB_VECTOR_FILE, TYPEDM_ADJECTIVE_VECTOR_FILE, \
    TYPEDM_VERB_ADJECTIVE_SIMILAR, TYPEDM_VERB_ADJECTIVE_SIMILAR_JSON, \
    GOOGLE_ADVERB_VECTOR_FILE, GOOGLE_VERB_ADVERB_SIMILAR, \
    GOOGLE_VERB_ADVERB_SIMILAR_JSON, GOOGLE_VERB_NOUN_SIMILAR, \
    GOOGLE_VERB_NOUN_SIMILAR_JSON, GOOGLE_NOUN_VECTOR_FILE, \
    GOOGLE_ARTICLE_VECTOR_FILE, GOOGLE_VERB_ARTICLE_SIMILAR, \
    GOOGLE_CONJUNC_VECTOR_FILE, GOOGLE_CONJUNC_VERB_SIMILAR, \
    GOOGLE_NOUN_VERB_SIMILAR, GOOGLE_NOUN_VERB_SIMILAR_JSON, \
    GOOGLE_NOUN_ADJECTIVE_SIMILAR, GOOGLE_NOUN_ADJECTIVE_SIMILAR_JSON, \
    GOOGLE_NOUN_ADVERB_SIMILAR, GOOGLE_NOUN_ADVERB_SIMILAR_JSON
from preprocess.calculate_neighbors import CalculateNeighbors


class Get_Similarity_Thread(multiprocessing.Process):
    def __init__(self, begin, end, word_list_1, word_list_2, normalized_1, normalized_2, no_of_neighbors, similar_words):
        multiprocessing.Process.__init__(self)
        self.begin = begin
        self.end = end
        self.word_list_1 = word_list_1
        self.word_list_2 = word_list_2
        self.normalized_1 = normalized_1
        self.normalized_2 = normalized_2
        self.no_of_neighbors = no_of_neighbors
        self.similar_words = similar_words
    
    def run(self):
        for i in xrange(self.begin, self.end):
            if i % 10 == 0:
                print i
            word_1 = self.word_list_1[i]
            similarities = [CalculateNeighbors.dot_similarity(self.normalized_1[word_1], self.normalized_2[word_2])  for word_2 in self.word_list_2]
            nth_largest = heapq.nlargest(self.no_of_neighbors, similarities)[-1]
            most_similar_indices = [index for index in xrange(len(similarities)) if similarities[index] >= nth_largest]
            self.similar_words[word_1] = [(self.word_list_2[index], similarities[index]) for index in most_similar_indices if self.word_list_2[index] != word_1]
            self.similar_words[word_1] = sorted(self.similar_words[word_1], key=lambda x : x[1])

class Save_To_Readable_Thread(multiprocessing.Process):
    def __init__(self, file_name, word_list_1, neighbor_number, similar_words, pos_type_1, pos_type_2):
        multiprocessing.Process.__init__(self)
        self.file_name = file_name
        self.word_list_1 = word_list_1
        self.neighbor_number = neighbor_number
        self.similar_words = similar_words
        self.pos_type_1 = pos_type_1
        self.pos_type_2 = pos_type_2
    
    def run(self):
        print 'save_to_readable_file ' + self.file_name
        with codecs.open(self.file_name, 'w', 'UTF-8') as filehandler:
            for word_1 in self.similar_words.keys():
                for word_2, similarity in self.similar_words[word_1][-self.neighbor_number:]:
                    filehandler.write(word_1)
                    filehandler.write('-' + self.pos_type_1 + '\t')
                    filehandler.write(word_2)
                    filehandler.write('-' + self.pos_type_2 + '\t')
                    filehandler.write(str(similarity))
                    filehandler.write('\n')
                                
class CalculateNeighborsTwoTypes(CalculateNeighbors):
    '''
    classdocs
    '''


    def __init__(self, vector_file_1, vector_file_2, type_1='v', type_2='j'):
        '''
        vector_file_1: Vector files for words that are need to find neighbors
        vector_file_2: Vector files for words that are neighbors to words in vector_file_1
        '''
        self.vector_file_1 = vector_file_1
        self.vector_file_2 = vector_file_2
        
        with codecs.open(vector_file_1, 'r', 'UTF-8') as filehandler:
            self.vector_data_1 = json.load(filehandler)
            
        with codecs.open(vector_file_2, 'r', 'UTF-8') as filehandler:
            self.vector_data_2 = json.load(filehandler)
        
        self.type_1 = type_1
        self.type_2 = type_2
            
    def find_k_nearest_neighbors(self, k, no_of_thread=8):
        print 'find_k_nearest_neighbors ' + str(k)
        self.normalized_1 = dict()
        self.normalized_2 = dict()
        self.k = k
        self.dim = 0
        
        for word in self.vector_data_1:
            t = numpy.array(self.vector_data_1[word])
            self.normalized_1[word] = t / numpy.sqrt(t.dot(t)) 
            if self.dim == 0:
                self.dim = len(self.normalized_1[word])
                
        for word in self.vector_data_2:
            t = numpy.array(self.vector_data_2[word])
            self.normalized_2[word] = t / numpy.sqrt(t.dot(t))
        
        manager = Manager()
        self.similar_words = manager.dict()
        
        self.word_list_1 = [word for word in self.normalized_1]
        self.word_list_2 = [word for word in self.normalized_2 if word not in self.word_list_1]
        
        print len(self.word_list_1)
                
        step = long(len(self.word_list_1) / (no_of_thread - 1))
        threads = []
        for i in xrange(no_of_thread):
            start = i * step
            end = numpy.min([(i + 1) * step, len(self.word_list_1)])
            print str(start) + " " + str(end)
            this_thread = Get_Similarity_Thread(start, end, self.word_list_1, self.word_list_2, \
                                                 self.normalized_1, self.normalized_2, self.k, self.similar_words)
            this_thread.start()
            threads.append(this_thread)
        
        for thread in threads:
            thread.join()
    
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
                                                   neighbor_number, self.similar_words, self.type_1, self.type_2)
            this_thread.start()
            threads.append(this_thread)
        
        for thread in threads:
            thread.join()
                    
if __name__ == '__main__':
#     neighbor_finder = CalculateNeighborsTwoTypes(GOOGLE_VERB_VECTOR_FILE, GOOGLE_ADVERB_VECTOR_FILE, type_1='v', type_2='a')
#     neighbor_finder.find_k_nearest_neighbors(100)
#     neighbor_finder.save_to_json_file(GOOGLE_VERB_ADVERB_SIMILAR_JSON)
#     neighbor_finder.save_to_readable_file(GOOGLE_VERB_ADVERB_SIMILAR)
    
#     neighbor_finder = CalculateNeighborsTwoTypes(GOOGLE_ARTICLE_VECTOR_FILE, GOOGLE_VERB_VECTOR_FILE, type_1='a', type_2='v')
#     neighbor_finder.find_k_nearest_neighbors(500)
#     neighbor_finder.save_to_json_file(GOOGLE_VERB_ARTICLE_SIMILAR_JSON)
#     neighbor_finder.save_to_readable_file(GOOGLE_VERB_ARTICLE_SIMILAR)
    
#     neighbor_finder = CalculateNeighborsTwoTypes(GOOGLE_CONJUNC_VECTOR_FILE, GOOGLE_VERB_VECTOR_FILE, type_1='cj', type_2='v')
#     neighbor_finder.find_k_nearest_neighbors(100)
# #     neighbor_finder.save_to_json_file(GOOGLE_VERB_ARTICLE_SIMILAR_JSON)
#     neighbor_finder.save_to_readable_file(GOOGLE_CONJUNC_VERB_SIMILAR)
    
#     neighbor_finder = CalculateNeighborsTwoTypes(TYPEDM_VERB_VECTOR_FILE, TYPEDM_ADJECTIVE_VECTOR_FILE)
#     neighbor_finder.find_k_nearest_neighbors(100)
#     neighbor_finder.save_to_readable_file(TYPEDM_VERB_ADJECTIVE_SIMILAR)
#     neighbor_finder.save_to_json_file(TYPEDM_VERB_ADJECTIVE_SIMILAR_JSON)
    
#     number_of_neighbors = 200
#     neighbors = [50, 75, 100, 200]
#     
#     neighbor_finder = CalculateNeighborsTwoTypes(GOOGLE_VERB_VECTOR_FILE, GOOGLE_NOUN_VECTOR_FILE, type_1='v', type_2='n')
#     neighbor_finder.find_k_nearest_neighbors(number_of_neighbors)
#     neighbor_finder.save_to_readable_file(GOOGLE_VERB_NOUN_SIMILAR, neighbors)
#     neighbor_finder.save_to_json_file(GOOGLE_VERB_NOUN_SIMILAR_JSON, neighbors)
#      
#     neighbor_finder = CalculateNeighborsTwoTypes(GOOGLE_VERB_VECTOR_FILE, GOOGLE_ADJECTIVE_VECTOR_FILE, type_1='v', type_2='a')
#     neighbor_finder.find_k_nearest_neighbors(number_of_neighbors)
#     neighbor_finder.save_to_readable_file(GOOGLE_VERB_ADJECTIVE_SIMILAR, neighbors)
#     neighbor_finder.save_to_json_file(GOOGLE_VERB_ADJECTIVE_SIMILAR_JSON, neighbors)
#     
#     neighbor_finder = CalculateNeighborsTwoTypes(GOOGLE_VERB_VECTOR_FILE, GOOGLE_ADVERB_VECTOR_FILE, type_1='v', type_2='adv')
#     neighbor_finder.find_k_nearest_neighbors(number_of_neighbors)
#     neighbor_finder.save_to_readable_file(GOOGLE_VERB_ADVERB_SIMILAR, neighbors)
#     neighbor_finder.save_to_json_file(GOOGLE_VERB_ADVERB_SIMILAR_JSON, neighbors)
    
    number_of_neighbors = 200
    neighbors = [25, 50, 100, 200]
    
    neighbor_finder = CalculateNeighborsTwoTypes(GOOGLE_NOUN_VECTOR_FILE, GOOGLE_VERB_VECTOR_FILE, type_1='n', type_2='v')
    neighbor_finder.find_k_nearest_neighbors(number_of_neighbors)
    neighbor_finder.save_to_readable_file(GOOGLE_NOUN_VERB_SIMILAR, neighbors)
    neighbor_finder.save_to_json_file(GOOGLE_NOUN_VERB_SIMILAR_JSON, neighbors)
     
    neighbor_finder = CalculateNeighborsTwoTypes(GOOGLE_NOUN_VECTOR_FILE, GOOGLE_ADJECTIVE_VECTOR_FILE, type_1='n', type_2='a')
    neighbor_finder.find_k_nearest_neighbors(number_of_neighbors)
    neighbor_finder.save_to_readable_file(GOOGLE_NOUN_ADJECTIVE_SIMILAR, neighbors)
    neighbor_finder.save_to_json_file(GOOGLE_NOUN_ADJECTIVE_SIMILAR_JSON, neighbors)
    
    neighbor_finder = CalculateNeighborsTwoTypes(GOOGLE_NOUN_VECTOR_FILE, GOOGLE_ADVERB_VECTOR_FILE, type_1='n', type_2='adv')
    neighbor_finder.find_k_nearest_neighbors(number_of_neighbors)
    neighbor_finder.save_to_readable_file(GOOGLE_NOUN_ADVERB_SIMILAR, neighbors)
    neighbor_finder.save_to_json_file(GOOGLE_NOUN_ADVERB_SIMILAR_JSON, neighbors)
