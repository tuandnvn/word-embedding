'''
Created on Mar 4, 2015

@author: Tuan Do
'''
import sys

import numpy

from util import TYPEDM_VERB_SIMILAR_JSON
from relativeGraph.build_graph import BuildGraph
from relativeGraph.graph import Edge


class BuildMultiParentGraph(BuildGraph):
    '''
    classdocs
    '''


    def __init__(self, similar_file, parent_index):
        '''
        Constructor
        '''
        BuildGraph.__init__(self, similar_file)
        
        self.parent_index = parent_index
        
    def build_edges(self, target_word, node_dict):
        edges = []
        for i in xrange(len(self.similar_words[target_word])):
            c_word, _ = self.similar_words[target_word][i]
            if (c_word, target_word) in self.similar_index:
                similarity = self.similar_index[(c_word, target_word)]
            else:
                similarity = -sys.maxint
            
            similarities = []
            similarities.append((target_word, similarity))
            
            for j in xrange(i + 1, len(self.similar_words[target_word])):
                b_word_candidate, _ = self.similar_words[target_word][j]
                if (c_word, b_word_candidate) in self.similar_index:
                    similarities.append((b_word_candidate, self.similar_index[(c_word, b_word_candidate)]))
                    
            similarities = sorted(similarities, key=lambda x : x[1], reverse=True)
            
            selected_number = numpy.min([self.parent_index, len(similarities)])
            selected = similarities[:selected_number]
            
            for b_word_candidate, similarity in selected:
                edges.append(Edge(node_dict[b_word_candidate], node_dict[c_word], {'weight': similarity}))
                
        return edges

if __name__ == '__main__':
    verb_adj_simi_separator = BuildMultiParentGraph(TYPEDM_VERB_SIMILAR_JSON, 2)
    
    words = ['build', 'eat', 'cook', 'kill']
    for word in words:
        g = verb_adj_simi_separator.build_graph(word)
        g.save_to_gdf(word + '.gdf')
