'''
Created on Mar 4, 2015

@author: Tuan Do
'''
from utils import TYPEDM_VERB_SIMILAR_JSON, GOOGLE_VERB_SIMILAR_JSON
from relativeGraph.build_graph import BuildGraph
from relativeGraph.graph import Edge


class BuildAbsoluteGraph(BuildGraph):
    '''
    classdocs
    '''


    def __init__(self, similar_file):
        '''
        Constructor
        '''
        BuildGraph.__init__(self, similar_file)
            
    def build_edges(self, target_word, node_dict):
        edges = []
        for word_1,_ in self.similar_words[target_word]:
            for word_2,_ in self.similar_words[target_word]:
                if word_1 != word_2:
                    if (word_1, word_2) in self.similar_index:
                        edges.append(Edge(node_dict[word_1], node_dict[word_2], {'weight': self.similar_index[(word_1, word_2)]}))
        return edges

if __name__ == '__main__':
    verb_simi_separator = BuildAbsoluteGraph(GOOGLE_VERB_SIMILAR_JSON)
    
    words = ['build', 'eat', 'cook', 'kill']
    for word in words:
        g = verb_simi_separator.build_graph(word)
        g.save_to_gdf(word + '.gdf')