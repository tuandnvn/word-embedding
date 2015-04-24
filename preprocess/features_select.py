'''
Created on Feb 25, 2015

@author: Tuan Do
'''
import codecs
import heapq
import json

import numpy

from utils import FRAMENET_VERB_CLASS, FRAMENET_VERB_VECTOR, AGG_AVERAGE, \
    FRAMENET_SELECTED_FEATURES_VERB_VECTOR
from cluster.word_cluster import WordCluster


class Features_Select(object):
    '''
    '''

    def __init__(self, verb_class_file, vector_file, verb_vector_selected_file, agg_average_file):
        '''
        Constructor
        '''
        with codecs.open(verb_class_file, 'r', 'UTF-8') as filehandler:
            self.verb_class_dict = json.load(filehandler)
            
        with codecs.open(vector_file, 'r', 'UTF-8') as filehandler:
            self.vector_data_1 = json.load(filehandler)
        
        self.verb_vector_selected_file = verb_vector_selected_file
        self.agg_average_file = agg_average_file
        
        self.dim = 0
        
    def process_to_agg_average_file(self):
        
        def diff_function(vector_1, vector_2):
            return vector_1 - vector_2
        
        def cos_function(vector_1, vector_2):
            return vector_1 * vector_2
            
        def average_squared_function(vectors):
            if len(vectors) > 0:
                size = len(vectors[0])
                result = numpy.zeros(size)
                for vector in vectors:
                    result += vector * vector
                return result / len(vectors)
        
        def average_function(vectors):
            if len(vectors) > 0:
                size = len(vectors[0])
                result = numpy.zeros(size)
                for vector in vectors:
                    result += vector
                return result
            
        self.normalized_1 = dict()
        
        for verb in self.vector_data_1:
            verb_adj_simi_separator = numpy.array(self.vector_data_1[verb])
            self.normalized_1[verb] = verb_adj_simi_separator / numpy.sqrt(verb_adj_simi_separator.dot(verb_adj_simi_separator)) 
            if self.dim == 0:
                self.dim = len(self.normalized_1[verb])
        
        agg_average_dist_centroid = numpy.zeros(self.dim)
        
        counter = 0
        for frame_name in self.verb_class_dict:
            counter += 1
#             if counter > 2:
#                 break
            words = self.verb_class_dict[frame_name]
            
            cluster = numpy.zeros((len(words), self.dim))
            for i in xrange(len(words)):
                verb = words[i]
                cluster[i] = self.normalized_1[verb]
            
            if len(words) != 0:
                word_cluster = WordCluster(frame_name, words, cluster, cos_function, average_function)
                average_dist_centroid = word_cluster.average_dist_centroid
                
                agg_average_dist_centroid += average_dist_centroid
        
        with codecs.open(self.agg_average_file, 'w', 'UTF-8') as filehandler:
            json.dump(list(agg_average_dist_centroid), filehandler)
            
    def keep_feature(self, no_of_features):
        with codecs.open(self.agg_average_file, 'r', 'UTF-8') as filehandler:
            agg_average_dist_centroid = json.load(filehandler)
            
#         nth_smallest = heapq.nsmallest(no_of_features, agg_average_dist_centroid)[-1]
#         smallest_feature_indices = [index for index in xrange(len(agg_average_dist_centroid)) if agg_average_dist_centroid[index] <= nth_smallest]
#         print smallest_feature_indices
        
        nth_largest = heapq.nlargest(no_of_features, agg_average_dist_centroid)[-1]
        largest_feature_indices = [index for index in xrange(len(agg_average_dist_centroid)) if agg_average_dist_centroid[index] >= nth_largest]
        
        verb_vector_selected = dict()
        for verb in self.vector_data_1:
            verb_vector_selected[verb] = [self.vector_data_1[verb][index] for index in largest_feature_indices]
        with codecs.open(self.verb_vector_selected_file, 'w', 'UTF-8') as filehandler:
            json.dump(verb_vector_selected, filehandler)
            
        
selector = Features_Select(FRAMENET_VERB_CLASS, FRAMENET_VERB_VECTOR, FRAMENET_SELECTED_FEATURES_VERB_VECTOR, AGG_AVERAGE)
selector.process_to_agg_average_file()
selector.keep_feature(1000)