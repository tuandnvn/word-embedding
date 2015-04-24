'''
Created on Mar 7, 2015

@author: Tuan Do
'''
import codecs
import json
import struct

from matplotlib.colors import ColorConverter
from mpl_toolkits.mplot3d import Axes3D
from numpy import linalg
import numpy

from utils import GOOGLE_VERB_VECTOR_FILE, GOOGLE_DATA_300K
import matplotlib.pyplot as plt
from preprocess.google import GoogleData


class SynAntonym(object):
    '''
    classdocs
    '''


    def __init__(self, vector_file = None, raw_file = None):
        '''
        Constructor
        '''
        self.vector_data = {}
        if vector_file != None:
            self.vector_file = vector_file
            
            with codecs.open(vector_file, 'r', 'UTF-8') as filehandler:
                self.vector_data = json.load(filehandler)
            
            self.normalized_1 = dict()
            
            self.dim = None
            for verb in self.vector_data:
                if self.dim == None:
                    self.dim = len(self.vector_data[verb])
                verb_adj_simi_separator = numpy.array(self.vector_data[verb])
                self.normalized_1[verb] = verb_adj_simi_separator / numpy.sqrt(verb_adj_simi_separator.dot(verb_adj_simi_separator))
            
            self.vector_data = self.normalized_1
        
        if raw_file != None:
            self.raw_file = raw_file
            self.vector_data = GoogleData.read_raw_file(self.raw_file)
            print 'Finish loading raw file'
            
        self.color_converter = ColorConverter()
    
    def represent_syn_ant_nym(self, target_verb, senses, keep_dim=2, include_target = False):
        assert keep_dim == 2 or keep_dim == 3
        words = set()
        if include_target:
            words.add(target_verb)
        
        color_dict = dict()
        color_dict[target_verb] = 'k'
        
        colors = ['b', 'g', 'r', 'c', 'm', 'y', 'firebrick', u'#FBC15E', u'#8dd3c7', u'#30a2da', u'#fdb462', u'#467821']
        
        for i in xrange(len(senses)):
            syns, antos = senses[i]
            for synonym in syns:
                if synonym not in self.vector_data:
                    break
                words.add(synonym)
#                 color_dict[synonym] = self.color_converter.cache[self.color_converter.cache.keys()[2 * i]]
                color_dict[synonym] = colors[2 * i]
            for antonym in antos:
                if antonym not in self.vector_data:
                    break
                words.add(antonym)
#                 color_dict[antonym] = self.color_converter.cache[self.color_converter.cache.keys()[2 * i + 1]]
                color_dict[antonym] = colors[2 * i + 1]
        
        words = list(words)
        
        self.dim = len(self.vector_data[self.vector_data.keys()[0]])
        data = numpy.zeros((len(words), self.dim))
        for i in xrange(len(words)):
            data[i] = self.vector_data[words[i]]
        
        U, _, _ = linalg.svd(data)
        newdata = U[:, :keep_dim]
        
        fig = plt.figure()
        
        if keep_dim == 2:
            ax = fig.add_subplot(1, 1, 1)
            
            for i in xrange(len(words)):
                ax.scatter(newdata[i, 0], newdata[i, 1], color=color_dict[words[i]])
            for i in xrange(len(words)):
                ax.annotate(words[i], (newdata[i, 0], newdata[i, 1]))
        elif keep_dim == 3:
            ax = fig.add_subplot(1, 1, 1, projection='3d')
            
            for i in xrange(len(words)):
                ax.scatter(newdata[i, 0], newdata[i, 1], newdata[i, 2], color=color_dict[words[i]])
            for i in xrange(len(words)):
                ax.text(newdata[i, 0], newdata[i, 1], newdata[i, 2], words[i])
                
        plt.xlabel('SVD1')
        plt.ylabel('SVD2')
        plt.show()

if __name__ == '__main__':
    target_verb = 'build'
    senses = [(['construct', 'make', 'raise', 'assemble', 'erect', 'fabricate', 'form'],
               ['dismantle', 'demolish']),
              (['establish', 'start', 'begin', 'found', 'base', 'institute', 'constitute', 'initiate', 'originate', 'formulate', 'inaugurate'],
               ['end', 'finish', 'suspend', 'relinquish']),
              (['develop', 'increase', 'improve', 'extend', 'strengthen', 'intensify', 'enlarge', 'amplify', 'augment'],
               ['reduce', 'contract', 'lower', 'decline', 'harm', 'weaken', 'decrease', 'dilute', 'impair', 'sap', 'debilitate'])]
    
#     target_verb = 'reveal'
#     senses = [(['disclose', 'tell', 'announce', 'publish', 'broadcast', 'leak', 'communicate', 'proclaim', 'betray', 'impart', 'divulge'],
#               ['hide', 'conceal', 'cover']),
#               (['show', 'display', 'bare', 'exhibit', 'unveil', 'uncover', 'manifest', 'unearth', 'unmask'],
#                [])]
    
    target_verb = 'hold'
    senses = [(['support', 'take', 'bear', 'shoulder', 'sustain', 'prop', 'brace'],
                ['break', 'give', 'loosen']),
               (['restrain', 'constrain', 'check', 'bind', 'curb', 'hamper', 'hinder'],
                ['free', 'release']),
               (['consider', 'think', 'believe', 'view', 'judge', 'regard', 'maintain', 'assume', 'reckon', 'esteem', 'deem', 'presume'],
                ['deny', 'reject', 'refute', 'disavow', 'disclaim']),
               (['possess', 'have', 'own', 'bear', 'retain'],
                ['offer', 'bestow']),
                (['conduct', 'convene', 'have', 'call', 'run', 'celebrate', 'carry', 'assemble'],
                ['cancel', 'postpone'])]
    
    target_verb = 'size'
    senses = [(['large','big','huge','gigantic','tremendous','enormous'\
                ,'gargantuan','vast','immense','colossal','mammoth'],\
               ['small','tiny','little',\
              'minute','wee','dwarf','meager','microscopic',\
              'diminutive','petite','infinitesimal'])]
                
#     verb_adj_simi_separator = SynAntonym(vector_file = GOOGLE_VERB_VECTOR_FILE)
    verb_adj_simi_separator = SynAntonym(raw_file = GOOGLE_DATA_300K) 
    verb_adj_simi_separator.represent_syn_ant_nym(target_verb, senses, 2)

    target_verb = 'temperature'
    senses = [(['hot','boiling','scorching','lukewarm','balmy'\
                ,'mild','warm'],\
               ['frozen','cold','icy',\
              'arctic','cool','frosty','chilly','frigid'])]
    
    verb_adj_simi_separator.represent_syn_ant_nym(target_verb, senses, 2)
    
    target_verb = 'humidity'
    senses = [(['dry','desiccated','dehydrated','parched','torrid'\
                ,'arid'],\
               ['watery','soggy','humid',\
              'soaked','damp','moist','wet'])]
    
    verb_adj_simi_separator.represent_syn_ant_nym(target_verb, senses, 2)