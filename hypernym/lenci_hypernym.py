'''
Created on Mar 26, 2015

@author: Tuan Do
'''
from _collections import defaultdict
import codecs
import json

import numpy

from utils import LENCI_BLESS, GOOGLE_NOUN_SIMILAR_JSON, \
    GOOGLE_NOUN_VERB_SIMILAR_JSON, GOOGLE_NOUN_ADJECTIVE_SIMILAR_JSON, \
    GOOGLE_NOUN_ADVERB_SIMILAR_JSON, VERB, ADJ, NOUN, ADV, WORD, SEMANTIC_TYPE, \
    RANDOM_N, MERO, HYPER, COORD, RANKS, LENCI_WORD_RANKS
from calculate_average_precision import Average_Precision
from plurality import get_plural_form
from separate_anto_syno.separate_anto_syno import Separate_Anto_Syno


class Lenci_Hypernym(object):
    '''
    classdocs
    '''


    def __init__(self, hypernym_file, no_of_neighbor = 100):
        '''
        Constructor
        '''
        self.hypernym_file = hypernym_file
        self.all_words = {}
        self.no_of_neighbor = no_of_neighbor
        self.read_hypernym_file()
    
    def load_separators(self, compare_type):
        self.separators = {}
        if compare_type == 'verb':
            file_name = GOOGLE_NOUN_VERB_SIMILAR_JSON.replace(".json", "." + str(self.no_of_neighbor) + ".json")
            self.separators[VERB] = Separate_Anto_Syno(file_name)
        elif compare_type == 'adj':
            file_name = GOOGLE_NOUN_ADJECTIVE_SIMILAR_JSON.replace(".json", "." + str(self.no_of_neighbor) + ".json")
            self.separators[ADJ] = Separate_Anto_Syno(file_name)
        elif compare_type == 'noun':
            file_name = GOOGLE_NOUN_SIMILAR_JSON.replace(".json", "." + str(self.no_of_neighbor) + ".json")
            self.separators[NOUN] = Separate_Anto_Syno(file_name)
        elif compare_type == 'adv':
            file_name = GOOGLE_NOUN_ADVERB_SIMILAR_JSON.replace(".json", "." + str(self.no_of_neighbor) + ".json")
            self.separators[ADV] = Separate_Anto_Syno(file_name)
            
    def read_hypernym_file(self):
        with codecs.open(self.hypernym_file, 'r', 'UTF-8') as filehandler:
            for line in filehandler:
                '''alligator-n    amphibian_reptile    attri    aggressive-j'''
                word_pos, semantic_type, rel_type, rel_word_pos = line.strip().split('\t')
                word, _ = word_pos.split('-')
                
                if not word in self.all_words:
                    self.all_words[word] = {WORD:word, SEMANTIC_TYPE:semantic_type}
                    
                try:
                    rel_word, _ = rel_word_pos.split('-')
                    
                    if rel_type not in self.all_words[word]:
                        self.all_words[word][rel_type] = []
                    self.all_words[word][rel_type].append(rel_word)
                except ValueError:
                    pass
    
    def change_set_to_list(self):
        for word in self.all_words:
            for rel_type in [RANDOM_N, MERO, HYPER, COORD]:
                if rel_type in self.all_words[word]:
                    self.all_words[word][rel_type] = list(self.all_words[word][rel_type])
                else:
                    self.all_words[word][rel_type] = []
                
    def print_all_words(self):
        word_set = set()
        for target_word in self.all_words:
            word_set.add(target_word)
#             for rel_type in [HYPER]:
            for rel_type in [RANDOM_N, MERO, HYPER, COORD]:
                for word in self.all_words[target_word][rel_type]:
                    word_set.add(word)
        for word in word_set:
            print word
            
    def hypernym_direction(self, rank_file):
        with codecs.open(rank_file, 'r', 'UTF-8') as filehandler:
            self.word_ranks = json.load(filehandler)
            
        total_counter = 0
        hypernym_counter = 0
        has_value_counter = 0
        for target_word in self.all_words:
            for candidate_word in self.all_words[target_word][HYPER]:
                target_word_plural = get_plural_form(target_word)
                candidate_word_plural = get_plural_form(candidate_word)
                
                if candidate_word_plural not in self.word_ranks:
                    candidate_word_plural = candidate_word
                if target_word_plural not in self.word_ranks:
                    target_word_plural = target_word
                
                if target_word in self.word_ranks and candidate_word in self.word_ranks:
                    total_counter += 1
                    target_rel_rank = float(self.word_ranks[target_word])/self.word_ranks[target_word_plural]
                    candidate_rel_rank = float(self.word_ranks[candidate_word])/self.word_ranks[candidate_word_plural]
                    
                    if target_rel_rank < 0.15:
                        target_word_plural = target_word
                    
                    if  candidate_rel_rank < 0.15:
                        candidate_word_plural = candidate_word
                         
                    if target_word in self.word_ranks and target_word_plural in self.word_ranks \
                        and candidate_word in self.word_ranks and candidate_word_plural in self.word_ranks:
                        
                        target_rel_rank = float(self.word_ranks[target_word])/self.word_ranks[target_word_plural]
                        candidate_rel_rank = float(self.word_ranks[candidate_word])/self.word_ranks[candidate_word_plural]
                        
                        target_rel_rank /= numpy.log(self.word_ranks[target_word])
                        candidate_rel_rank /= numpy.log(self.word_ranks[candidate_word])
                        
                        has_value_counter += 1
                        if target_rel_rank < candidate_rel_rank:
                            hypernym_counter += 1
                        else:
                            print '-----------------------------'
                            print target_word + " " + target_word_plural + " " + candidate_word + " " + candidate_word_plural
                            print str(self.word_ranks[target_word]) + " " + str(self.word_ranks[target_word_plural]) + " "\
                                +str(self.word_ranks[candidate_word]) + " " + str(self.word_ranks[candidate_word_plural])
                            print str(numpy.log(1000 + self.word_ranks[target_word])) + ' ' + str(numpy.log(1000 + self.word_ranks[candidate_word]))
                            print str(target_rel_rank) + ' ' + str(candidate_rel_rank)
                else:
                    print target_word  + " " + candidate_word 
        
        print "total_counter " + str(total_counter)
        print "has_value_counter " + str(has_value_counter)
        print "hypernym_counter " + str(hypernym_counter)
        print float(hypernym_counter)/ total_counter
        print float(hypernym_counter)/ has_value_counter
                    
    
    def sort(self, compare_type=VERB):
        separator = self.separators[compare_type]
        
        for word in self.all_words:
            list_of_candidates = self.all_words[word][MERO] +  self.all_words[word][COORD]\
                             +  self.all_words[word][RANDOM_N] +  self.all_words[word][HYPER]
            l = separator.sort(word, list_of_candidates)
        
            similarities = list(set([entry[1] for entry in l]))
            similarities.sort(key=lambda x : -x)
            similarity_dict = defaultdict(list)
            for candidate, similarity in l:
                similarity_dict[similarity].append(candidate)
            ranks = []
            for similarity in similarities:
                if len(similarity_dict[similarity]) == 1:
                    ranks.append(similarity_dict[similarity][0])
                else:
                    ranks.append(similarity_dict[similarity])
            
            print ranks
            self.all_words[word][RANKS] = ranks
        print len(self.all_words.keys())
    
    def get_average_ap(self):
        self.all_word_list = [self.all_words[word] for word in self.all_words]
        print len(self.all_word_list)
        t = Average_Precision(self.all_word_list)
        
        print t.calculate_average_ap_values()
        
if __name__ == '__main__':
    t = Lenci_Hypernym(LENCI_BLESS)
#     t.print_all_words()
    t.hypernym_direction(LENCI_WORD_RANKS)
#     t.change_set_to_list()
#     
#     compare_type=NOUN
#     t.load_separators(compare_type)
#     t.sort(compare_type)
#      
#     t.get_average_ap()