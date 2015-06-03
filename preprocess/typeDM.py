'''
Created on Feb 5, 2015

@author: Tuan Do
'''
import codecs

import numpy

from util import TENSOR_FILENAME, SVD_FILENAME, NEAREST_NEIGHBOR_FILENAME, \
    VERB_SVD_FILENAME, ADJECTIVE_SVD_FILENAME, ADJECTIVES, NOUNS
from cluster.cluster import Cluster


class TypeDM(object):
    '''
    classdocs
    '''


    def __init__(self, tensor_file_name, svd_file_name, neighbor_file_name):
        '''
        Constructor
        '''
        self.tensor_file_name = tensor_file_name
        self.svd_file_name = svd_file_name
        self.neighbor_file_name = neighbor_file_name
        
    def filter_svd_file(self, output_svd_file_name, function):
        '''
        This method process the svd file
        that filter over each line of svd_file
        '''
        outputs = []
        counter = 0
        with codecs.open(self.svd_file_name, 'r', 'UTF-8') as filehandler:
            for line in filehandler:
                output_line = function(line.strip())
                if output_line != None:
                    counter += 1
                    outputs.append(output_line)
                    if counter % 10 == 0:
                        print counter
#                 if (counter > 100):
#                     break
                
        with codecs.open(output_svd_file_name, 'w', 'UTF-8') as filehandler:
            for output_line in outputs:
                filehandler.write(output_line)
                filehandler.write('\n')
                
    def extract_word(self, output_word_file, function):
        words = []
        with codecs.open(self.svd_file_name, 'r', 'UTF-8') as filehandler:
            for line in filehandler:
                word = function(line.strip())
                if word != None:
                    print word
                    words.append(word)
        with codecs.open(output_word_file, 'w', 'UTF-8') as filehandler:
            for word in words:
                filehandler.write(word)
                filehandler.write('\n')
    
    @staticmethod
    def filter_line_noun_only(input_line):
        space_index = input_line.find('\t')
        word = input_line[:space_index]
        values = word.split('-')
        if values[1] == 'n':
            return input_line
        return None
    
    @staticmethod
    def filter_line_verb_only(input_line):
        space_index = input_line.find('\t')
        word = input_line[:space_index]
        values = word.split('-')
        if values[1] == 'v':
            return input_line
        return None
    
    @staticmethod
    def filter_line_adjective_only(input_line):
        space_index = input_line.find('\t')
        word = input_line[:space_index]
        values = word.split('-')
        if values[1] == 'j':
            return input_line
        return None
    
    @staticmethod
    def extract_adjective(input_line):
        space_index = input_line.find('\t')
        word = input_line[:space_index]
        values = word.split('-')
        if values[1] == 'j':
            return values[0]
        return None
    
    @staticmethod
    def extract_noun(input_line):
        space_index = input_line.find('\t')
        word = input_line[:space_index]
        values = word.split('-')
        if values[1] == 'n':
            return values[0]
        return None
    
    def create_cluster(self, verb_matrix_file, verbset):
        '''
        verbset: VerbSet that has a verbclass_dict
        '''
        
        # A dictionary from a verb to a numpy array representing the verb 
        verb_to_dm_repr = {}
        no_of_col = 0
        with codecs.open(verb_matrix_file, 'r', 'UTF-8') as filehandler:
            for input_line in filehandler:
                space_index = input_line.strip().find('\t')
                word = input_line[:space_index]
                values = word.split('-')
                verb = values[0]
                values_str = input_line[space_index:].split('\t')
                values = [int(value) for value in values_str]
                verb_to_dm_repr[verb] = numpy.array(values)
                if no_of_col == 0:
                    no_of_col = len(values)
        
        clusters = []        
        for rel_name in verbset.verbclass_dict:
            list_of_verbs = self.verbclass_dict[rel_name]
            matrix = numpy.array((len(list_of_verbs), no_of_col))
            for i in xrange(len(list_of_verbs)):
                matrix[i] = verb_to_dm_repr[list_of_verbs[i]]
            cluster = Cluster(rel_name, matrix, list_of_verbs)
            clusters.append(cluster)
            
        return clusters
    
    
typeDM_processor = TypeDM(TENSOR_FILENAME, SVD_FILENAME, NEAREST_NEIGHBOR_FILENAME)

# typeDM_processor.filter_svd_file(VERB_SVD_FILENAME, TypeDM.filter_line_verb_only) 
# typeDM_processor.filter_svd_file(ADJECTIVE_SVD_FILENAME, TypeDM.filter_line_adjective_only)
# typeDM_processor.extract_word(ADJECTIVES, TypeDM.extract_adjective)
# typeDM_processor.filter_svd_file(ADVERB_SVD_FILENAME, TypeDM.filter_line_adverb_only)
typeDM_processor.extract_word(NOUNS, TypeDM.extract_noun)