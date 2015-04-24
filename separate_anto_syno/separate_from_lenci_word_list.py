'''
Created on Mar 24, 2015

@author: Tuan Do
'''
from _collections import defaultdict
import codecs

from utils import GOOGLE_VERB_SIMILAR_JSON, GOOGLE_VERB_ADJECTIVE_SIMILAR_JSON, \
    GOOGLE_VERB_NOUN_SIMILAR_JSON, GOOGLE_VERB_ADVERB_SIMILAR_JSON, \
    LENCI_SYNONYM_FILE, LENCI_ANTONYM_FILE, VERB, ADJ, NOUN, ADV, WORD, ANTONYMS, \
    SYNONYMS, RANKS
from calculate_average_precision import Average_Precision
from separate_anto_syno import Separate_Anto_Syno


class Lenci_Process(object):
    '''
    classdocs
    '''


    def __init__(self, antonym_verb_file, synonym_verb_file, no_of_neighbor = 100):
        '''
        Constructor
        '''
        self.antonym_verb_file = antonym_verb_file
        self.synonym_verb_file = synonym_verb_file
        
        self.no_of_neighbor = no_of_neighbor
        self.all_words = {}
    
    def load_separators(self, compare_type):
        self.separators = {}
        
        if compare_type == 'verb':
            file_name = GOOGLE_VERB_SIMILAR_JSON.replace(".json", "." + str(self.no_of_neighbor) + ".json")
            self.separators[VERB] = Separate_Anto_Syno(file_name)
        elif compare_type == 'adj':
            file_name = GOOGLE_VERB_ADJECTIVE_SIMILAR_JSON.replace(".json", "." + str(self.no_of_neighbor) + ".json")
            self.separators[ADJ] = Separate_Anto_Syno(file_name)
        elif compare_type == 'noun':
            file_name = GOOGLE_VERB_NOUN_SIMILAR_JSON.replace(".json", "." + str(self.no_of_neighbor) + ".json")
            self.separators[NOUN] = Separate_Anto_Syno(file_name)
        elif compare_type == 'adv':
            file_name = GOOGLE_VERB_ADVERB_SIMILAR_JSON.replace(".json", "." + str(self.no_of_neighbor) + ".json")
            self.separators[ADV] = Separate_Anto_Syno(file_name)
        
    def preprocess_antonym_file(self):
        with codecs.open(self.antonym_verb_file, 'r', 'UTF-8') as filehandler:
            for line in filehandler:
                query_form, result_form = line.strip().split('\t')
                if result_form == '0':
                    continue
                
                query_form = query_form[3:]
                result_form = result_form[3:]
                
                # Skip phrasal verb
                if result_form.find('_') != -1:
                    continue
                
                if query_form not in self.all_words:
                    self.all_words[query_form] = {}
                    self.all_words[query_form][WORD] = query_form
                
                if ANTONYMS not in self.all_words[query_form]:
                    self.all_words[query_form][ANTONYMS] = set()
                
                self.all_words[query_form][ANTONYMS].add(result_form)
                
        print "Done preprocess antonym file"
    
    def preprocess_synonym_file(self):
        with codecs.open(self.synonym_verb_file, 'r', 'UTF-8') as filehandler:
            for line in filehandler:
                query_form, result_form = line.strip().split('\t')
                if result_form == '0':
                    continue
                
                query_form = query_form[3:]
                result_form = result_form[3:]
                
                # Skip phrasal verb
                if result_form.find('_') != -1:
                    continue
                
                if query_form not in self.all_words:
                    self.all_words[query_form] = {}
                    self.all_words[query_form][WORD] = query_form
                
                if SYNONYMS not in self.all_words[query_form]:
                    self.all_words[query_form][SYNONYMS] = set()
                
                self.all_words[query_form][SYNONYMS].add(result_form)
        
        print "Done preprocess synonym file"
        
    def print_all_words(self):
        word_set = set()
        for target_word in self.all_words:
            word_set.add(target_word)
            if SYNONYMS in self.all_words[target_word]:
                for word in self.all_words[target_word][SYNONYMS]:
                    word_set.add(word)
            if ANTONYMS in self.all_words[target_word]:
                for word in self.all_words[target_word][ANTONYMS]:
                    word_set.add(word)
        for word in word_set:
            print word
    
    def change_set_to_list(self):
        for word in self.all_words:
            if SYNONYMS in self.all_words[word]:
                self.all_words[word][SYNONYMS] = list(self.all_words[word][SYNONYMS])
            else:
                self.all_words[word][SYNONYMS] = []
            if ANTONYMS in self.all_words[word]:
                self.all_words[word][ANTONYMS] = list(self.all_words[word][ANTONYMS])
            else:
                self.all_words[word][ANTONYMS] = []
                
    def sort(self, compare_type=VERB):
        separator = self.separators[compare_type]
        
        for word in self.all_words:
            l = separator.sort(word, self.all_words[word][SYNONYMS] +  self.all_words[word][ANTONYMS])
            print word + " " + str(l)
        
            similarities = list(set([entry[1] for entry in l]))
            similarities.sort()
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
    
    def sort_according_to_neighbor(self):
        separator = self.separators[VERB]
        
        for word in self.all_words:
            l = separator.sort_simple(word,  self.all_words[word][SYNONYMS] + self.all_words[word][ANTONYMS])
            print word + " " + str(l)
        
            ranks = [entry[0] for entry in l]
            self.all_words[word][RANKS] = ranks
        print len(self.all_words.keys())
    
    def get_average_ap(self):
        self.all_word_list = [self.all_words[word] for word in self.all_words]
        print len(self.all_word_list)
        t = Average_Precision(self.all_word_list)
        
        print t.calculate_average_ap_values()
        
if __name__ == '__main__':
    t = Lenci_Process(LENCI_ANTONYM_FILE, LENCI_SYNONYM_FILE, 200)
    t.preprocess_antonym_file()
    t.preprocess_synonym_file()
#     t.print_all_words()
    t.change_set_to_list()
     
    compare_type=VERB
    t.load_separators(compare_type)
    t.sort(compare_type)
#     t.sort_according_to_neighbor()
     
    t.get_average_ap()
