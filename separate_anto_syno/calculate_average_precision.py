'''
Created on Mar 24, 2015

@author: Tuan Do
'''
import numpy


WORD = "word"
ANTONYMS = "antonyms"
SYNONYMS = "synonyms"
RANKS = "ranks"
    
class Average_Precision(object):
    '''
    classdocs
    '''

    def __init__(self, verb_struct):
        '''
        verb_struct = a list of dictionary
        each entry is a dict():
            - "word" : verb word
            - "antonyms" : [] list of antonyms
            - "synonyms" : [] list of synonyms
            - "ranks" : list of antonyms and synonyms mixed and ranked based on some method
                " The rank should be sorted so that antonyms should be earlier in the list "
            "ranks" could have list entry, for example:
                [sleep, [eat, drink]] if eat and drink has the same rank
        '''
        self.verb_struct = verb_struct
        
    def calculate_ap_values(self):
        antonym_ap_values = []
        synonym_ap_values = []
        for entry in self.verb_struct:
            word = entry[WORD]
            antonyms = entry[ANTONYMS]
            synonyms = entry[SYNONYMS]
            ranks = entry[RANKS]
            
            if len(ranks) == 0:
                continue
            
            print "-------------------------"
            print word
            
            accumulate_sum_antonyms = 0
            accumulate_sum_synonyms = 0
            accumulate_antonyms = 0
            accumulate_synonyms = 0
           
            print "Antonyms " + str(antonyms)
            print "Synonyms " + str(synonyms)
            print ranks
            
            for i in xrange(len(ranks)):
                if type(ranks[i]) == list:
                    words = ranks[i]
                    number_of_antonyms = len([ word for word in words if word in antonyms ])
                    number_of_synonyms = len([ word for word in words if word in synonyms ])
                    accumulate_antonyms += number_of_antonyms
                    accumulate_synonyms += number_of_synonyms
                    accumulate_sum_antonyms += number_of_antonyms * float(accumulate_antonyms) /(accumulate_antonyms + accumulate_synonyms)
                    accumulate_sum_synonyms += number_of_synonyms * float(accumulate_synonyms) /(accumulate_antonyms + accumulate_synonyms)
                else:
                    word = ranks[i]
                    if word in antonyms:
                        accumulate_antonyms += 1
                        accumulate_sum_antonyms += float(accumulate_antonyms) /(accumulate_antonyms + accumulate_synonyms)
                    if word in synonyms:
                        accumulate_synonyms += 1
                        accumulate_sum_synonyms += float(accumulate_synonyms) /(accumulate_antonyms + accumulate_synonyms)
            
            print str(accumulate_antonyms) + " " + str(accumulate_sum_antonyms)
            print str(accumulate_synonyms) + " " + str(accumulate_sum_synonyms)
            if accumulate_antonyms == 0:
                antonym_ap_value = 0.5
            else:
                antonym_ap_value = accumulate_sum_antonyms/ accumulate_antonyms
                
            if accumulate_synonyms == 0:
                synonym_ap_value = 0.5
            else:
                synonym_ap_value = accumulate_sum_synonyms/ accumulate_synonyms
            
            antonym_ap_values.append(antonym_ap_value)
            synonym_ap_values.append(synonym_ap_value)
            
            print str(antonym_ap_value) + " " + str(synonym_ap_value)
        
        return (antonym_ap_values, synonym_ap_values)
    
    def calculate_average_ap_values(self):
        antonym_ap_values, synonym_ap_values = self.calculate_ap_values()
        return numpy.average(antonym_ap_values),numpy.average(synonym_ap_values) 