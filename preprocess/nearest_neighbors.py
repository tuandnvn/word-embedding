'''
Created on Feb 23, 2015

@author: Tuan Do
'''
from _collections import defaultdict
import codecs
import json

from utils import NEAREST_NEIGHBOR_FILENAME, FRAMENET_VERB_CLASS, \
    VERB_SIMILAR_FRAMENET_ONLY


class NearestNeighbor(object):
    '''
    classdocs
    '''


    def __init__(self, nearest_neigbor_file, verb_class_file):
        '''
        Constructor
        '''
        
        with codecs.open(verb_class_file, 'r', 'UTF-8') as filehandler:
            self.verb_class_dict = json.load(filehandler)
            
        self.indexing()
        self.read_neighbors(nearest_neigbor_file)
            
    def indexing(self):
        self.verb_to_frames = defaultdict(list)
        for frame_name in self.verb_class_dict:
            for verb in self.verb_class_dict[frame_name]:
                self.verb_to_frames[verb].append(frame_name)
        
        self.verb_to_same_frame_verbs = defaultdict(set)
        for verb in self.verb_to_frames:
            for frame_name in self.verb_to_frames[verb]:
                self.verb_to_same_frame_verbs[verb] = self.verb_to_same_frame_verbs[verb].union(set(self.verb_class_dict[frame_name])) 
            
                
    def read_neighbors(self, nearest_neigbor_file):
        self.nearest_neighbor = defaultdict(list)
        with codecs.open(nearest_neigbor_file, 'r', 'UTF-8') as filehandler:
            for line in filehandler:
                values = line.strip().split()
                target = values[0].split('-')[0]
                target_pos = values[0].split('-')[1]
                
                neighbor = values[1].split('-')[0]
                neighbor_pos = values[1].split('-')[1]
                
                if target_pos == 'v' and neighbor_pos == 'v':
                    self.nearest_neighbor[target].append(neighbor)
        
                if target == 'scold':
                    print line
        with codecs.open('tempo_1.txt', 'w', 'UTF-8') as filehandler:
            for target in self.nearest_neighbor:
                if target in self.verb_to_same_frame_verbs:
                    filehandler.write('--------------------------------------------------\n')
                    filehandler.write( target)
                    filehandler.write('\n')
                    filehandler.write('--- Words in same frames\n')
                    frame_set = set(self.verb_to_same_frame_verbs[target])
                    neighbors = [str(verb) for verb in self.nearest_neighbor[target]]
                    filehandler.write(str([str(verb_adj_simi_separator) for verb_adj_simi_separator in list(frame_set)]))
                    filehandler.write('\n') 
                    filehandler.write('--- 10 nearest neighbors\n')
                    filehandler.write(str(neighbors))
                    filehandler.write('\n')
                    filehandler.write('--- Interception\n')
                    filehandler.write(str([str(verb_adj_simi_separator) for verb_adj_simi_separator in frame_set.intersection(set(neighbors))]))
                    filehandler.write('\n')
                    filehandler.write('--- Difference\n')
                    filehandler.write(str(set(neighbors).difference(frame_set)))
                    filehandler.write('\n')
                        
verb_adj_simi_separator = NearestNeighbor(VERB_SIMILAR_FRAMENET_ONLY, FRAMENET_VERB_CLASS)
