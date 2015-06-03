'''
Created on Mar 5, 2015

@author: Tuan Do
'''
import sys

from util import TYPEDM_VERB_SIMILAR_JSON
from relativeGraph.build_graph import BuildGraph
from relativeGraph.graph import Graph, Node, Edge


class Build_Set_Relative_Graph(BuildGraph):
    '''
    classdocs
    '''


    def __init__(self, similar_file):
        '''
        Constructor
        '''
        BuildGraph.__init__(self, similar_file)
        
#         self.normalized_similarity()
        
    def build_graph_multi(self, target_words):
        '''
        target_words : list of target_word
        '''
        node_dict, nodes = self.build_nodes_multi(target_words)
        edges = self.build_edges_multi(target_words, node_dict)
        return Graph(nodes, edges, ["word"], ["weight"])
    
    def build_nodes_multi(self, target_words):
        node_dict = dict()
        nodes = []
        
        set_of_words = set()
        for target_word in target_words:
            set_of_words.add(target_word)
        for index in xrange(len(self.similar_words[target_word])):
            word, _ = self.similar_words[target_word][index]
            set_of_words.add(word)
        
        index = 0
        for word in set_of_words:
            node = Node(index, {'word':word})
            node_dict[word] = index
            nodes.append(node)
            index += 1
            
        return node_dict, nodes
    
    def build_edges_multi(self, target_words, node_dict):
        edges = []
        
        set_of_words = set()
        for target_word in target_words:
            set_of_words.add(target_word)
        for index in xrange(len(self.similar_words[target_word])):
            word, _ = self.similar_words[target_word][index]
            set_of_words.add(word)
        list_of_words = list(set_of_words)
        
        for i in xrange(len(list_of_words)):
            c_word = list_of_words[i]
            if c_word in target_words:
                continue
            '''Select the verbs topological-in between verb and target_word'''
            '''b_word are in range [i + 1:] and also a'''
            
            similarity = None
            for target_word in target_words:
                if (c_word, target_word) in self.similar_index:
                    if similarity == None or similarity < self.similar_index[(c_word, target_word)]:
                        similarity = self.similar_index[(c_word, target_word)]
                        parent_candidate = target_word
                else:
                    if similarity == None:
                        similarity = -sys.maxint
                        parent_candidate = target_word
            
            
            for j in xrange(len(list_of_words)):
                if j == i:
                    continue
                b_word_candidate = list_of_words[j]
                
                if (c_word, b_word_candidate) in self.similar_index:
                    compared_similarity = self.similar_index[(c_word, b_word_candidate)]
                    
#                     for target_word in target_words:
#                         if (c_word, target_word) in self.similar_index and (b_word_candidate, target_word) in self.similar_index\
#                         and self.similar_index[(c_word, target_word)] > self.similar_index[(b_word_candidate, target_word)]:
#                             break
#                     else:
                    if compared_similarity > similarity:
                        similarity = compared_similarity
                        parent_candidate = b_word_candidate
            
            edges.append(Edge(node_dict[parent_candidate], node_dict[c_word], {'weight': similarity}))
        return edges
    
    
if __name__ == '__main__':
    verb_adj_simi_separator = Build_Set_Relative_Graph(TYPEDM_VERB_SIMILAR_JSON)
    
#     pairs = [['ban', 'permit'], ['build', 'destroy'], ['cry', 'smile']\
#              , ['construct', 'demolish'], ['open', 'close'], ['leave', 'arrive'],
#              ['kill', 'rescue'], ['lose', 'gain'], ['prohibit', 'allow']]
    pairs = [['kill', 'murder'], ['build', 'construct']]
    for target_pair in pairs:
        g = verb_adj_simi_separator.build_graph_multi(target_pair)
        g.save_to_gdf('_'.join(target_pair) + '.gdf')
