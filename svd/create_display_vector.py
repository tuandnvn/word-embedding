'''
Created on Mar 6, 2015

@author: Tuan Do
'''
import codecs
import json

import numpy

from utils import GOOGLE_VERB_VECTOR_FILE, GOOGLE_VERB_SIMILAR_JSON, TYPEDM_VERB_VECTOR, \
    TYPEDM_VERB_SIMILAR_JSON


class CreateInput(object):
    '''
    classdocs
    '''


    def __init__(self, vector_file, similar_file):
        '''
        Constructor
        '''
        self.vector_file = vector_file
        
        with codecs.open(vector_file, 'r', 'UTF-8') as filehandler:
            self.vector_data_1 = json.load(filehandler)
        
        self.normalized_1 = dict()
        for verb in self.vector_data_1:
            verb_adj_simi_separator = numpy.array(self.vector_data_1[verb])
            self.normalized_1[verb] = verb_adj_simi_separator / numpy.sqrt(verb_adj_simi_separator.dot(verb_adj_simi_separator))
        
        self.vector_data_1 = self.normalized_1
            
        with codecs.open(similar_file, 'r', 'UTF-8') as filehandler: 
            self.similar_words = json.load(filehandler)
            
    def save_to_file(self, target_word, output_file):
        with codecs.open(output_file + '.dat', 'w', 'UTF-8') as filehandler:
            for word in [verb_adj_simi_separator[0] for verb_adj_simi_separator in self.similar_words[target_word]] + [target_word]:
                vector_str = ','.join ([str(val) for val in self.vector_data_1[word]])
                filehandler.write(vector_str)
                filehandler.write('\n')
        with codecs.open(output_file, 'w', 'UTF-8') as filehandler:
            for word in [verb_adj_simi_separator[0] for verb_adj_simi_separator in self.similar_words[target_word]] + [target_word]: 
                filehandler.write(word)
                filehandler.write('\n')
                
if __name__ == '__main__':
    verb_adj_simi_separator = CreateInput(TYPEDM_VERB_VECTOR, TYPEDM_VERB_SIMILAR_JSON)
    verb_adj_simi_separator.save_to_file('kill', 'kill.txt')
    verb_adj_simi_separator.save_to_file('reveal', 'reveal.txt')
    verb_adj_simi_separator.save_to_file('build', 'build.txt')