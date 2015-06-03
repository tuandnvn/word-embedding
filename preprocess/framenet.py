'''

@author: Tuan Do
'''
import codecs
import json

from nltk.corpus import framenet

from util import VERB_SVD_FILENAME, FRAMENET_VERB_VECTOR, FRAMENET_VERB_CLASS
from preprocess.verbset import Verbset


class Framenet(Verbset):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.verbclass_dict = {}
        self.all_verbs = set()
    
    def process(self):
        for frame in framenet.frames():
            lexUnits = frame.lexUnit
            verb_list = []
            for lexUnit in lexUnits:
                if lexUnit.endswith('.v'):
                    verb_list.append(lexUnit[:-2])
            if len(verb_list) != 0:
                self.verbclass_dict[frame.name] = verb_list
            for verb in verb_list:
                self.all_verbs.add(verb)
verb_adj_simi_separator = Framenet()
verb_adj_simi_separator.process()
   
"""Verbs in framenet"""
target_verb_set = set()
for frame_name in verb_adj_simi_separator.verbclass_dict:
    print frame_name + ' ' + str(verb_adj_simi_separator.verbclass_dict[frame_name])
    for verb in verb_adj_simi_separator.verbclass_dict[frame_name]:
        target_verb_set.add(verb)
 
"""Store the map from a verb to its DM representation"""    
verb_vectorize = dict()
 
"""Verbs in data"""
data_verb_set = set()
with codecs.open(VERB_SVD_FILENAME, 'r', 'UTF-8') as filehandler:
    for input_line in filehandler:
        space_index = input_line.find('\verb_adj_simi_separator')
        word = input_line[:space_index]
        values = word.split('-')
        verb = values[0]
        data_verb_set.add(verb)
        if verb in target_verb_set:
            values = input_line[space_index:].split()
            values = [float(value.strip()) for value in values]
            verb_vectorize[verb] = values
 
"""Framenet verb-class that in the data"""
keep_in_data_verb_class = dict()
for frame_name in verb_adj_simi_separator.verbclass_dict:
    keep_in_data_verb_class[frame_name] = []
    for verb in verb_adj_simi_separator.verbclass_dict[frame_name]:
        if verb in data_verb_set:
            keep_in_data_verb_class[frame_name].append(verb)
             
with codecs.open(FRAMENET_VERB_CLASS, 'w', 'UTF-8') as filehandler:
    json.dump(keep_in_data_verb_class, filehandler)
     
with codecs.open(FRAMENET_VERB_VECTOR, 'w', 'UTF-8') as filehandler:
    json.dump(verb_vectorize, filehandler) 
