'''
Created on Mar 5, 2015

@author: Tuan Do
'''
import sys

from utils import TYPEDM_VERB_SIMILAR_JSON, GOOGLE_VERB_SIMILAR_JSON
from relativeGraph.build_graph import BuildGraph
from relativeGraph.build_relative_graph import BuildRelativeGraph
from relativeGraph.graph import Edge


class BuildIndependentGraph(BuildGraph):
    '''
    classdocs
    '''

    def __init__(self, similar_file):
        '''
        Constructor
        '''
        BuildGraph.__init__(self, similar_file)
        
#         self.normalized_similarity()
    
    def build_edges(self, target_word, node_dict):
        '''Words are sorted in increasing order of similarity to target_word'''
        
        target_word_similar_words = self.similar_words[target_word] + [(target_word, 1)]
        edges = []
        for i in xrange(len(target_word_similar_words)):
            c_word, _ = target_word_similar_words[i]
            '''Select the verbs topological-in between verb and target_word'''
            '''b_word are in range [i + 1:] and also a'''
            
            similarity = None
            parent_candidate = None
#             if (c_word, target_word) in self.similar_index:
#                 similarity = self.similar_index[(c_word, target_word)]
#             else:
#                 similarity = -sys.maxint
#             parent_candidate = target_word
            
            for j in xrange(len(target_word_similar_words)):
                if j == i:
                    continue
                b_word_candidate, _ = target_word_similar_words[j]
                if (c_word, b_word_candidate) in self.similar_index:
                    compared_similarity = self.similar_index[(c_word, b_word_candidate)]
                    if similarity == None or compared_similarity > similarity:
                        similarity = compared_similarity
                        parent_candidate = b_word_candidate
            
            edges.append(Edge(node_dict[parent_candidate], node_dict[c_word], {'weight': similarity}))
        return edges

if __name__ == '__main__':
    verb_simi_separator = BuildIndependentGraph(GOOGLE_VERB_SIMILAR_JSON)
#     verb_simi_separator = BuildIndependentGraph(VERB_SIMILAR_FRAMENET_ONLY_JSON_SELECTED_FEATURES)
    
    words = ['destroy', 'dismantle', 'demolish', 'raze']
    words = ['strengthen', 'enhance', 'solidify']
    words = ['topple', 'dislodge']
#     words = ['reveal']
    for word in words:
        g = verb_simi_separator.build_graph(word)
        g.save_to_gdf(word + '.gdf')
        
        