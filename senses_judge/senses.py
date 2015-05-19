'''
Created on May 4, 2015

@author: Tuan Do
'''
import codecs
import heapq

from future.utils import iteritems
import numpy


class Senses(object):
    '''
    classdocs
    '''


    def __init__(self, vocab_file, senses, vector_size):
        '''
        Constructor
        '''
        self.vocab_file = vocab_file
        self.vector_size = vector_size
        self.senses = senses
        self.read_vocab_file()
    
    def read_vocab_file(self):
        self.words = {}
        with codecs.open(self.vocab_file, 'r', 'UTF-8') as filehandler:
            counter = 0
            for line in filehandler:
                values = line.split()
                self.words[values[0]] = counter
                counter += 1
        self.vocab_size = len(self.words.keys())
        self.word_index = { u : v for v, u in iteritems(self.words)}
    
    def read_sense_vector_file_text(self, sense_vector_file):
        self.sense_vectors = numpy.zeros((self.vocab_size, self.senses, self.vector_size))
        word_index = 0
        with codecs.open(sense_vector_file, 'r', 'UTF-8') as filehandler:
            for line in filehandler:
                values = line.split()
                for i in xrange(self.senses):
                    for j in xrange(self.vector_size):
                        self.sense_vectors[word_index, i, j] = float(values [1 + i * self.vector_size + j])
                
                word_index += 1
                
        self.sense_vectors /= numpy.expand_dims(numpy.linalg.norm(self.sense_vectors, axis=2), 2) 
    
    def _examine_neighbors(self, word_index, sense_index, no_of_neighbors):
        similars = numpy.dot( self.sense_vectors, numpy.transpose(self.sense_vectors[word_index][sense_index]))
        nlargests = heapq.nlargest(no_of_neighbors, numpy.ndindex((self.vocab_size, self.senses)), similars.__getitem__)
        for vocab_index, sense_index in nlargests:
            print str(self.word_index[vocab_index]) + ' ' + str(sense_index)
            
    def examine_neighbors(self, word, no_of_neighbors, sense_index=None):
        word_index = self.words[word]
        if sense_index:
            self._examine_neighbors(word_index, sense_index, no_of_neighbors)
        else:
            for sense_index in xrange(self.senses):
                self._examine_neighbors(word_index, sense_index, no_of_neighbors)
                
        
    def examine_senses(self, word):
        word_index = self.words[word]
        for sense_index_1 in xrange(self.senses):
            for sense_index_2 in xrange(self.senses):
                if sense_index_1 != sense_index_2:
                    simi = numpy.dot(self.word_index[word_index, sense_index_1], self.word_index[word_index, sense_index_2])
                    print "%d %d %f" % (sense_index_1, sense_index_2, simi)

if __name__ == '__main__':
    from senses import Senses
    t = Senses('vocab.txt', 3, 100)
    t.read_sense_vector_file_text('multi_vectors.txt')
    
    t = Senses('vocab.txt', 1, 50)
    t.read_sense_vector_file_text('vectors.txt')