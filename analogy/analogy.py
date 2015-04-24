'''
Created on Mar 30, 2015

@author: Tuan Do
'''
import codecs
import heapq
import json
from multiprocessing import Manager
import multiprocessing
import struct

import numpy

from utils import ANALOGY_FILE, CAPITAL_COMMON_COUNTRIES, GOOGLE_DATA_300K

class Analogy(object):
    '''
    classdocs
    '''


    def __init__(self, vector_file_name, analogy_file_name):
        '''
        Constructor
        '''
        self.vector_file_name = vector_file_name
        self.analogy_file_name = analogy_file_name
        
        self.relations = {}
        
        self.manager = Manager()
    
    def read_vector_file(self):
        print 'Begin read vector file ' + self.vector_file_name
        self.word_vector = {}
        with open(self.vector_file_name, "rb") as filehandler:
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
            
            counter = 0
            print self.words
#             for _ in xrange(self.words):
            for _ in xrange(10000):
                tempo = ''
                while True:
                    char = filehandler.read(1)
                    if char == None or ord(char) == 32 or ord(char) == 10:
                        break
                    else:
                        tempo += char
                word = tempo
                
                if counter % 100 == 0:
                    print counter
                counter += 1
                
                vector = [0] * self.dim
                for a in xrange(self.dim):
                    vector[a] = struct.unpack("f", filehandler.read(4))[0]
                
                self.word_vector[word] = numpy.array(vector)
        self.word_list = self.word_vector.keys()
    
    @staticmethod
    def additive(word_vector, word_1, word_2, word_3):
        return word_vector[word_2] + word_vector[word_3] - word_vector[word_1]
    
    @staticmethod
    def weight_additive(word_1, word_2, word_3, alpha):
        return word_2 + alpha * word_3 - alpha * word_1
    
    @staticmethod
    def log_additive(word_1, word_2, word_3):
        return word_2 * word_3 / word_1
    
    @staticmethod
    def log_weight_additive(word_1, word_2, word_3, alpha):
        if alpha > 0:
            return word_2 * numpy.power(word_3, alpha) / numpy.power(word_1, alpha)
    
    def calculate_analogy(self, word_1, word_2, word_3, function, no_of_neighbors):
        for word in [word_1, word_2, word_3]:
            if not word in self.word_vector:
                print word + ' not in word vector'
                return None
        
        result_vector = function(self.word_vector, word_1, word_2, word_3)
        
        similarities = [numpy.dot(result_vector, self.word_vector[word])  for word in self.word_list]
        nth_largest = heapq.nlargest(no_of_neighbors + 1, similarities)[-1]
        most_similar_indices = [index for index in xrange(len(similarities)) if similarities[index] >= nth_largest]
        word_ranks = [(self.word_list[index], similarities[index])\
                       for index in most_similar_indices if self.word_list[index] != word_3]
        word_ranks = sorted(word_ranks, key=lambda x : x[1])
        result = []
        result.append((word_1, word_2, word_3))
        result.append(word_ranks)
        return result
    
    def batch_calculate_analogy(self, list_of_word_triples, no_of_neighbors, result):
        function = Analogy.additive
        for t in list_of_word_triples:
            word_1, word_2, word_3 = t
            word_ranks = self.calculate_analogy(word_1, word_2, word_3, function, no_of_neighbors)
            if word_ranks != None:
                print word_ranks
                result += [word_ranks]
    
    def batch_calculate_analogy_multi_thread(self, list_of_word_triples, \
                                              no_of_neighbors, no_of_thread=4):
        self.raw_results = self.manager.dict()
        
        step = int(len(list_of_word_triples) / (no_of_thread - 1))
        threads = []
        for i in xrange(no_of_thread):
            start = i * step
            self.raw_results[i] = []
            end = numpy.min([(i + 1) * step, len(list_of_word_triples)])
            this_thread = multiprocessing.Process(target=self.batch_calculate_analogy, \
                                                args=(list_of_word_triples[start:end], \
                                                       no_of_neighbors, self.raw_results[i]))
            threads.append(this_thread)
        
        print 'thread start'
        for this_thread in threads:
            this_thread.start()
            
        for this_thread in threads:
            this_thread.join()
        print 'thread end'
        
        self.results = []
        for i in self.raw_results.keys():
            for result in self.raw_results[i]:
                self.results.append(result)
                
        print self.results
    
    def save_result_to_json_file(self, file_name):
        with codecs.open(file_name, 'w', 'UTF-8') as filehandler: 
            json.dump(self.results, filehandler)    
        
    def read_analogy_file(self):
        with codecs.open(self.analogy_file_name, 'r', 'utf-8') as file_handler:
            current_relation = None
            for line in file_handler:
                if line.strip()[:1] == ':':
                    current_relation = line.strip()[1:].strip()
                    self.relations[current_relation] = []
                else:
                    self.relations[current_relation].append(line.strip().split())
#         print self.relations[CAPITAL_COMMON_COUNTRIES]
        
        self.capital_countries = set()
        for capital_1, country_1, capital_2, country_2 in self.relations[CAPITAL_COMMON_COUNTRIES]:
            self.capital_countries.add((capital_1, country_1))
            self.capital_countries.add((capital_2, country_2))
        
if __name__ == '__main__':
#     manager = Manager()
#     d = manager.dict()
#     for i in xrange(2):
#         d[i] = manager.list((1,2,3,4))
#         d[i] += [2,3]
#     for i in xrange(2):
#         for j in d[i]:
#             print j
    t = Analogy(GOOGLE_DATA_300K, ANALOGY_FILE)
    t.read_vector_file()
    t.read_analogy_file()
     
    list_of_word_triples = [[u'Athens', u'Greece', u'Baghdad'],\
                            [u'Athens', u'Greece', u'Bangkok'],\
                            [u'Athens', u'Greece', u'Beijing'],\
                            [u'Athens', u'Greece', u'Berlin'],\
                            [u'Athens', u'Greece', u'Bern'],\
                            [u'Athens', u'Greece', u'Cairo'],\
                            [u'Athens', u'Greece', u'Canberra'],\
                             [u'London', u'England', u'Hanoi'],\
                              [u'Athens', u'Greece', u'Havana'],\
                               [u'Athens', u'Greece', u'Helsinki'],\
                            [u'London', u'England', u'Islamabad'],\
                             [u'Athens', u'Greece', u'Kabul'],\
                              [u'Madrid', u'Spain', u'London'],\
                               [u'Moscow', u'Russia', u'Madrid'],\
                            [u'Ottawa', u'Canada', u'Moscow'],\
                             [u'Athens', u'Greece', u'Oslo'],\
                              [u'Athens', u'Greece', u'Ottawa'],\
                                      ]
    t.batch_calculate_analogy_multi_thread(list_of_word_triples,\
                                            no_of_neighbors=20, no_of_thread=2)
