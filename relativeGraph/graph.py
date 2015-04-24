'''
Created on Mar 3, 2015

@author: Tuan Do
'''
import codecs
from string import Formatter


class Graph(object):
    def __init__(self, nodes, edges, node_attrs, edge_attrs):
        self.nodes = nodes
        self.edges = edges
        self.id_to_nodes = dict()
        for node in self.nodes:
            self.id_to_nodes[node.id] = node
        self.node_attrs = node_attrs
        self.edge_attrs = edge_attrs
    
    def save_to_json(self, file_name):
        self.graph = dict()
        self.graph['node'] = dict()
        
        for node in self.nodes:
            self.graph['node'][node.id] = node.attrs
            
        self.graph['edge'] = [edge.get_json() for edge in self.edges]
        
    def save_to_gdf(self, file_name):
        '''
        nodedef>name VARCHAR,label VARCHAR
        s1,Site number 1
        s2,Site number 2
        s3,Site number 3
        edgedef>node1 VARCHAR,node2 VARCHAR, weight DOUBLE
        s1,s2,1.2341
        s2,s3,0.453
        s3,s2, 2.34
        s3,s1, 0.871
        '''
        f = Formatter()
        with codecs.open(file_name, 'w', 'UTF-8') as filehandler:
            filehandler.write('nodedef>name VARCHAR,')
            append = ','.join(attr + ' VARCHAR' for attr in self.node_attrs)
            filehandler.write(append)
            filehandler.write('\n')
            for node in self.nodes:
                filehandler.write(str(node.attrs['word']))
                filehandler.write(',')
                append = ','.join(node.attrs[attr] for attr in self.node_attrs)
                filehandler.write(append)
                filehandler.write('\n')
            filehandler.write('edgedef>node1 VARCHAR,node2 VARCHAR,')
            append = ','.join(attr + ' DOUBLE' for attr in self.edge_attrs)
            filehandler.write(append)
            filehandler.write('\n')
            for edge in self.edges:
                filehandler.write(str(self.id_to_nodes[edge.source].attrs['word']))
                filehandler.write(',')
                filehandler.write(str(self.id_to_nodes[edge.target].attrs['word']))
                filehandler.write(',')
                append = ','.join(str(edge.attrs[attr]) for attr in self.edge_attrs)
                filehandler.write(append)
                filehandler.write('\n')
            
    
class Node(object):
    '''
    classdocs
    '''

    def __init__(self, identity, attrs):
        '''
        Constructor
        '''
        self.id = identity
        self.attrs = attrs

class Edge(object):
    
    def __init__(self, source, target, attrs):
        '''
        Constructor
        source : id of Node
        target : id of Node
        '''
        self.source = source
        self.target = target
        self.attrs = attrs
        
    def get_json(self):
        values = dict()
        for attribute in self.attributes:
            values[attribute] = self.attributes[attribute]
        values['source'] = self.source
        values['key'] = self.key
        return values