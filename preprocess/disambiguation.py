'''
Created on Feb 23, 2015

@author: Tuan Do
'''
from _collections import defaultdict
import codecs
import json

from utils import FRAMENET_VERB_CLASS, FRAMENET_VERB_VECTOR


class Disambiguation(object):
    '''
    Disambiguation a verb form to its corresponding verbs 
    in multiple frames if the verbs is ambiguous
    '''

    def __init__(self, verb_class_file, vector_file):
        '''
        Constructor:
        verb_class_file: json dump of a dict() from frame_name to a list of verbs
        vector_file: json dump of a dict() from verb to a list of float values
        '''
        with codecs.open(verb_class_file, 'r', 'UTF-8') as filehandler:
            self.verb_class_dict = json.load(filehandler)
            
#         with codecs.open(verb_vector_file, 'r', 'UTF-8') as filehandler:
#             self.verb_vector_data = json.load(filehandler)
    
    def collapse_class(self):
        
        def isSubsetOf(list_1, list_2):
            if set(list_1).issubset(set(list_2)):
                return True
            return False
        
        print len(self.verb_class_dict)
        self.collapsed_verb_class_dict = dict()
        
        for frame_name in self.verb_class_dict:
            for frame_name_2 in self.verb_class_dict:
                if frame_name != frame_name_2 and len(self.verb_class_dict[frame_name]) != 0 and len(self.verb_class_dict[frame_name_2]) != 0:
                    if isSubsetOf(self.verb_class_dict[frame_name], self.verb_class_dict[frame_name_2]):
                        if frame_name < frame_name_2:
                            collapsed_name = frame_name + ' - ' + frame_name_2
                        else:
                            collapsed_name = frame_name_2 + ' - ' + frame_name
                        self.collapsed_verb_class_dict[collapsed_name] = self.verb_class_dict[frame_name_2]
                        
        print len(self.collapsed_verb_class_dict)
        for collapsed_frame_name in  self.collapsed_verb_class_dict:
            print collapsed_frame_name + ' ' + str(self.collapsed_verb_class_dict[collapsed_frame_name])
                        
            
    def indexing(self):
        self.ambiguous_verbs = []
        verb_to_frames = defaultdict(list)
        for frame_name in self.verb_class_dict:
            for verb in self.verb_class_dict[frame_name]:
                verb_to_frames[verb].append(frame_name)
        
        """225/604 is undisambiguable"""
        for frame_name in self.verb_class_dict:
            undisambiguable = all([len(verb_to_frames[verb]) > 1 for verb in self.verb_class_dict[frame_name]])
            if undisambiguable:
                print frame_name
                print self.verb_class_dict[frame_name]
                print [verb_to_frames[verb] for verb in self.verb_class_dict[frame_name]]
        
    
verb_adj_simi_separator = Disambiguation(FRAMENET_VERB_CLASS, FRAMENET_VERB_VECTOR)
verb_adj_simi_separator.collapse_class()
