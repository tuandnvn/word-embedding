'''
Created on Feb 4, 2015

@author: Tuan Do
'''
import codecs
import glob
import json

from util import VERBCLASS_DIR, VERB_DICT, VERBS
from preprocess.verbset import Verbset


class Verbnet(Verbset):
    '''
    classdocs
    
    '''
    
    def __init__(self, verbclass_dir):
        '''
        Constructor
        '''
        self.verbclass_dir = verbclass_dir
        
    def preprocess(self):
        files = glob.glob(self.verbclass_dir + "*.txt")
        
        self.verbclass_dict = {}
        self.all_verbs = set()
        
        for file_name in files:
            rel_name = file_name[file_name.rfind('\\')+1:len(file_name)-8]
            print rel_name
            list_of_verbs = []
            with codecs.open(file_name, 'r', 'UTF-8') as filehandler:
                for line in filehandler:
                    verb = (str)(line.strip())
                    list_of_verbs.append(verb) 
                    self.all_verbs.add(verb)
            
            self.verbclass_dict[rel_name] = list_of_verbs
    
    def save_to_json_file(self, file_name):
        with codecs.open(file_name, 'w', 'UTF-8') as filehandler:
            json.dump(self.verbclass_dict, filehandler)
            
    def save_verb_to_file(self, file_name):
        verbs = set()
        for rel_name in self.verbclass_dict:
            for verb in self.verbclass_dict[rel_name]:
                verbs.add(verb)
        with codecs.open(file_name, 'w', 'UTF-8') as filehandler:
            for verb in verbs:
                filehandler.write(verb)
                filehandler.write('\n')
            
v = Verbnet(VERBCLASS_DIR + "\\")
v.preprocess()
v.save_to_json_file(VERB_DICT)
v.save_verb_to_file(VERBS)