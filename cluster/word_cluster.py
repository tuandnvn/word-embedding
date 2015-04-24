'''
Created on Feb 5, 2015

@author: Tuan Do
'''
import math

import numpy


class WordCluster(object):
    '''
    classdocs
    '''


    def __init__(self, identity, words, cluster, distance_function, average_function):
        '''
        Constructor
        '''
        self.cluster = cluster
        self.distance_function = distance_function
        self.identity = identity
        self.words = words
        self.aggregate = numpy.array(self.cluster[0])
#         print words
        for i in xrange(1, len(self.cluster)):
            self.aggregate += self.cluster[i]
#         print '------------Centroid----------------------'
        self.centroid = self.aggregate / float(len(self.cluster))
#         print self.centroid
#         print '------------Distances-----------------'
        distances = [distance_function(self.centroid, item) for item in self.cluster]
#         print distances
#         print '-----------Avg------------------'
        self.average_dist_centroid = average_function(distances)
#         print self.average_dist_centroid
        
    def get_distance(self, other_cluster):
        '''
        other_cluster : WordCluster
        '''
        return self.distance_function(self.centroid, other_cluster.centroid)

def cos_function(vector_1, vector_2):
    return vector_1 * vector_2

        
def average_function(vectors):
    if len(vectors) > 0:
        size = len(vectors[0])
        result = numpy.zeros(size)
        for vector in vectors:
            result += vector
        return result / len(vectors)
    
a = numpy.array([[1,2,3],[4,5,6]])
verb_adj_simi_separator = WordCluster('a', ['b', 'c'], a, cos_function, average_function)