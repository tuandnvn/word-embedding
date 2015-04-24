'''
Created on Mar 24, 2015

@author: Tuan Do
'''
from _collections import defaultdict

import numpy

from utils import WORD, RANKS, RANDOM_N, MERO, HYPER, COORD


class Average_Precision(object):
    '''
    classdocs
    '''

    def __init__(self, verb_struct):
        '''
        verb_struct = a list of dictionary
        each entry is a dict():
            - "word" : verb word
            - "mero" : [] list of meronyms
            - "hyper" : [] list of hypernyms
            - "coord" : [] list of sister terms
            - "random-n" : [] list of random terms
            - "ranks" : list of terms based on some ranking
            "ranks" could have list entry, for example:
                [sleep, [eat, drink]] if eat and drink has the same rank
        '''
        self.verb_struct = verb_struct
        
    def calculate_ap_values(self):
        rel_term_ap_values = defaultdict(list)
        for entry in self.verb_struct:
            word = entry[WORD]
            ranks = entry[RANKS]
            
            if len(ranks) == 0:
                continue
            
            print "-------------------------"
            print word
            
            accumulate_sum = defaultdict(int)
            accumulate_count = defaultdict(int)
           
            for rel in [RANDOM_N, MERO, HYPER, COORD]:
                print rel + str(entry[rel])
            print ranks
            
            accumulate_count_for_all_rel = 0
            for i in xrange(len(ranks)):
                if type(ranks[i]) == list:
                    words = ranks[i]
                    for rel in [RANDOM_N, MERO, HYPER, COORD]:
                        number_of_word_in_rel = len([ word for word in words if word in entry[rel]])
                        accumulate_count[rel] += number_of_word_in_rel
                        accumulate_count_for_all_rel += number_of_word_in_rel
                    for rel in [RANDOM_N, MERO, HYPER, COORD]:
                        accumulate_sum[rel] += number_of_word_in_rel * float(accumulate_count[rel]) / accumulate_count_for_all_rel
                else:
                    word = ranks[i]
                    for rel in [RANDOM_N, MERO, HYPER, COORD]:
                        if word in entry[rel]:
                            accumulate_count[rel] += 1
                            accumulate_count_for_all_rel += 1
                            accumulate_sum[rel] += float(accumulate_count[rel]) / accumulate_count_for_all_rel
            
            for rel in [RANDOM_N, MERO, HYPER, COORD]:
                print rel
                print str(accumulate_count[rel]) + " " + str(accumulate_sum[rel])
                if accumulate_count[rel] == 0:
                    rel_term_ap_values[rel].append(0.5)
                else:
                    rel_term_ap_values[rel].append(accumulate_sum[rel] / accumulate_count[rel])
            
        return rel_term_ap_values
    
    def calculate_average_ap_values(self):
        ap_values = self.calculate_ap_values()
        for rel in ap_values:
            print rel
            print numpy.average(ap_values[rel])
