'''
Created on Mar 4, 2015

@author: Tuan Do
'''
from util import TYPEDM_VERB_SIMILAR_JSON
from relativeGraph.build_relative_graph import BuildRelativeGraph
from relativeGraph.graph import Edge


class BuildLinkedGraph(BuildRelativeGraph):
    '''
    classdocs
    '''


    def __init__(self, similar_file):
        '''
        Constructor
        '''
        BuildRelativeGraph.__init__(self, similar_file)
    
    def build_graph(self, target_word):
        graph = BuildRelativeGraph.build_graph(self, target_word)
        
        for edge in graph.edges:
            source = edge.source
            target = edge.target
            source_node = graph.id_to_nodes[source]
            target_node = graph.id_to_nodes[target]
            target_node.parent = source_node
        
        for node in graph.nodes:
            if 'parent' in node.__dict__:
                parent_node = node.parent
                if 'parent' in parent_node.__dict__:
                    grand_parent_node = parent_node.parent
                    if (grand_parent_node.attrs['word'], node.attrs['word']) in self.similar_index:
                        similarity = self.similar_index[(grand_parent_node.attrs['word'], node.attrs['word'])]
                        graph.edges.append(Edge(grand_parent_node.id, node.id, {'weight': similarity}))
                    
        return graph

if __name__ == '__main__':
    verb_adj_simi_separator = BuildLinkedGraph(TYPEDM_VERB_SIMILAR_JSON)
    
    words = ['build', 'eat', 'cook', 'kill']
    for word in words:
        g = verb_adj_simi_separator.build_graph(word)
        g.save_to_gdf(word + '.gdf')