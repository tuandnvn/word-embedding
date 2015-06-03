'''
Created on Mar 3, 2015

@author: Tuan Do
'''
import codecs
import json

from util import VERB_SVD_FILENAME, TYPEDM_VERB_VECTOR_FILE, \
    ADJECTIVE_SVD_FILENAME, TYPEDM_ADJECTIVE_VECTOR_FILE


class CalculateNeighbors(object):
    '''
    classdocs
    '''

    def __init__(self):
        pass
    
    def vectorize(self, text_file, json_file):
        verb_vectorize = dict()

        with codecs.open(text_file, 'r', 'UTF-8') as filehandler:
            for input_line in filehandler:
                space_index = input_line.find('\t')
                word = input_line[:space_index]
                values = word.split('-')
                verb = values[0]
                
                values = input_line[space_index:].split()
                values = [float(value.strip()) for value in values]
                verb_vectorize[verb] = values
                
        with codecs.open(json_file, 'w', 'UTF-8') as filehandler:
            json.dump(verb_vectorize, filehandler) 
        
if __name__ == '__main__':
    t = CalculateNeighbors()
#     t.vectorize(VERB_SVD_FILENAME, TYPEDM_VERB_VECTOR_FILE)
    t.vectorize(ADJECTIVE_SVD_FILENAME, TYPEDM_ADJECTIVE_VECTOR_FILE)