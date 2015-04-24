'''
Created on Mar 4, 2015

@author: Tuan Do
'''
import codecs
import json

import numpy

from relativeGraph.graph import Graph, Node


class BuildGraph(object):
    '''
    classdocs
    '''


    def __init__(self, similar_file):
        '''
        Constructor
        '''
        with codecs.open(similar_file, 'r', 'UTF-8') as filehandler: 
            self.similar_words = json.load(filehandler)
        self.similar_index = dict()
        for word_1 in self.similar_words:
            for word_2, similarity in self.similar_words[word_1]:
                self.similar_index[(word_1, word_2)] = similarity
            
    def normalized_similarity(self):
        '''normalized_for_each_term try to reduce the effect of close-to-all points
        For example, murder has relatively large similarity values for a lots of other verbs
        The reason is obscure.
        '''
        self.normalized_for_each_term = dict()
        
        for word_1 in self.similar_words:
            self.normalized_for_each_term[word_1] = numpy.average([sim for _, sim in self.similar_words[word_1]])
        for word_1 in self.similar_words:
            self.similar_words[word_1] = [(word_2, similarity / numpy.sqrt(self.normalized_for_each_term[word_1] * self.normalized_for_each_term[word_2])) \
                                          for word_2, similarity in self.similar_words[word_1]]
            self.similar_words[word_1] = sorted(self.similar_words[word_1], key=lambda x : x[1])
            
        for word_1 in self.similar_words:
            for word_2, similarity in self.similar_words[word_1]:
                self.similar_index[(word_1, word_2)] = similarity
    
    def build_nodes(self, target_word):
        node_dict = dict()
        nodes = []
        
        node = Node(0, {'word':target_word})
        node_dict[target_word] = 0
        nodes.append(node)
        for index in xrange(len(self.similar_words[target_word])):
            word, _ = self.similar_words[target_word][index]
            node = Node(index + 1, {'word':word})
            node_dict[word] = index + 1
            nodes.append(node)
            
        return node_dict, nodes
    
    def build_graph(self, target_word):
        node_dict, nodes = self.build_nodes(target_word)
        edges = self.build_edges(target_word, node_dict)
        return Graph(nodes, edges, ["word"], ["weight"])
