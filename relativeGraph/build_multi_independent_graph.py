'''
Created on Mar 6, 2015

@author: Tuan Do
'''
import numpy

from utils import GOOGLE_VERB_SIMILAR_JSON
from relativeGraph.build_graph import BuildGraph
from relativeGraph.graph import Edge


class BuildMultiIndependentGraph(BuildGraph):
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
        '''Words are sorted in increasing order of similarity to target_word'''
        edges = []
        for c_word in [verb_adj_simi_separator[0] for verb_adj_simi_separator in self.similar_words[target_word]] + [target_word]:
            '''Select the verbs topological-in between verb and target_word'''
            '''b_word are in range [i + 1:] and also a'''
            
            similarities = []
            for b_word_candidate in [verb_adj_simi_separator[0] for verb_adj_simi_separator in self.similar_words[target_word]] + [target_word]:
                if b_word_candidate == c_word:
                    continue
                if (c_word, b_word_candidate) in self.similar_index:
                    similarities.append((b_word_candidate, self.similar_index[(c_word, b_word_candidate)]))
                    
            similarities = sorted(similarities, key=lambda x : x[1], reverse=True)
            
            selected_number = numpy.min([self.parent_index, len(similarities)])
            selected = similarities[:selected_number]
            
            for b_word_candidate, similarity in selected:
                edges.append(Edge(node_dict[b_word_candidate], node_dict[c_word], {'weight': similarity}))
        return edges
    
    
if __name__ == '__main__':
    verb_adj_simi_separator = BuildMultiIndependentGraph(GOOGLE_VERB_SIMILAR_JSON, 2)
    
    words = ['build', 'eat', 'cook', 'kill']
    for word in words:
        g = verb_adj_simi_separator.build_graph(word)
        g.save_to_gdf(word + '.gdf')