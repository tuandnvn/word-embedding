'''
Created on Mar 3, 2015

@author: Tuan Do
'''
import sys

from util import VERB_SIMILAR_FRAMENET_ONLY_JSON, TYPEDM_VERB_SIMILAR_JSON, \
    VERB_SIMILAR_FRAMENET_ONLY_JSON_SELECTED_FEATURES, GOOGLE_VERB_SIMILAR_JSON
from relativeGraph.build_graph import BuildGraph
from relativeGraph.graph import Node, Edge, Graph


class BuildRelativeGraph(BuildGraph):
    '''
    classdocs
    '''


    def __init__(self, similar_file):
        '''
        Constructor
        '''
        BuildGraph.__init__(self, similar_file)
        
        self.normalized_similarity()
        
    def build_edges(self, target_word, node_dict):
        '''Words are sorted in increasing order of similarity to target_word'''
        edges = []
        for i in xrange(len(self.similar_words[target_word])):
            c_word, _ = self.similar_words[target_word][i]
            '''Select the verbs topological-in between verb and target_word'''
            '''b_word are in range [i + 1:] and also a'''
            if (c_word, target_word) in self.similar_index:
                similarity = self.similar_index[(c_word, target_word)]
            else:
                similarity = - sys.maxint
            parent_candidate = target_word
            
            for j in xrange(i + 1, len(self.similar_words[target_word])):
                b_word_candidate, _ = self.similar_words[target_word][j]
                if (c_word, b_word_candidate) in self.similar_index:
                    compared_similarity = self.similar_index[(c_word, b_word_candidate)]
                    if compared_similarity > similarity:
                        similarity = compared_similarity
                        parent_candidate = b_word_candidate
            
            edges.append(Edge(node_dict[parent_candidate], node_dict[c_word], {'weight': similarity}))
        return edges

if __name__ == '__main__':
    verb_simi_separator = BuildRelativeGraph(GOOGLE_VERB_SIMILAR_JSON)
#     verb_simi_separator = BuildRelativeGraph(VERB_SIMILAR_FRAMENET_ONLY_JSON_SELECTED_FEATURES)
    
    words = ['build', 'eat', 'cook', 'kill']
    for word in words:
        g = verb_simi_separator.build_graph(word)
        g.save_to_gdf(word + '.gdf')
