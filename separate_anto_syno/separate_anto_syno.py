'''
Created on Mar 9, 2015

@author: Tuan Do
'''
import codecs
import json

from util import GOOGLE_VERB_SIMILAR_JSON, GOOLGE_VERB_SIMILAR_INTERCEPT_INDEX, \
    GOOGLE_VERB_ADJECTIVE_SIMILAR_JSON, TYPEDM_VERB_SIMILAR_JSON, \
    TYPEDM_VERB_ADJECTIVE_SIMILAR_JSON, GOOGLE_VERB_ADVERB_SIMILAR_JSON, \
    GOOGLE_VERB_NOUN_SIMILAR_JSON
import matplotlib.pyplot as plt


class Separate_Anto_Syno(object):
    '''
    classdocs
    '''
    LABEL = 'label'
    INTERCEPTION_INDEX = 'interception_index'

    def __init__(self, similar_file, interception_file=None):
        '''
        Constructor
        '''
        with codecs.open(similar_file, 'r', 'UTF-8') as filehandler: 
            self.similar_words = json.load(filehandler)
        print '------Done load similar_file------'
        
        self.similar_index = dict()
        for word_1 in self.similar_words:
            for word_2, similarity in self.similar_words[word_1]:
                self.similar_index[(word_1, word_2)] = similarity
        print '------Done build similar index------'
        
        print Separate_Anto_Syno.interception_index(self.similar_words['open'], self.similar_words['close'])
#         print Separate_Anto_Syno.interception_index(self.similar_words['build'], self.similar_words['erect'])
#         self.load_interception_index(interception_file)
        
    def load_interception_index(self, interception_file):
        with codecs.open(interception_file, 'r', 'UTF-8') as filehandler: 
            self.interception_index_raw = json.load(filehandler)
        self.words = self.interception_index_raw[Separate_Anto_Syno.LABEL]
        self.interception_index = self.interception_index_raw[Separate_Anto_Syno.INTERCEPTION_INDEX]
        print self.interception_index[0][0]
        self.word_index_map = dict()
        for i in xrange(len(self.words)):
            self.word_index_map[self.words[i]] = i
             
        print '------Done load interception_index------'
    
    @staticmethod
    def interception_index(list_similarity_1, list_similarity_2):
        list_1 = [word_adj_simi_separator[0] for word_adj_simi_separator in list_similarity_1]
        list_2 = [word_adj_simi_separator[0] for word_adj_simi_separator in list_similarity_2]
        set_1 = set(list_1)
        set_2 = set(list_2)
#         print set_1.intersection(set_2)
        return len(set_1.intersection(set_2))
#         return float(len(set_1.intersection(set_2))) / (len(set_1.union(set_2)))
    
    @staticmethod
    def interception_set_index(set_1, set_2):
        return float(len(set_1.intersection(set_2))) / (len(set_1) + len(set_2))
    
    def build_interception_index(self, output_file):
        print '--------------build interception index-----------------'
        
        self.set_similar_words = dict()
        for word in self.similar_words:
            self.set_similar_words[word] = set([word_adj_simi_separator[0] for word_adj_simi_separator in self.similar_words[word]])
            
        self.interception_index = dict()
        count = 0
        for word_1 in self.similar_words:
            self.interception_index[word_1] = dict()
            count += 1
            if count % 10 == 0:
                print count
            for word_2 in self.similar_words:
                self.interception_index[word_1][word_2] = \
                 Separate_Anto_Syno.interception_set_index(self.set_similar_words[word_1], self.set_similar_words[word_2])
        
        with codecs.open(output_file, 'w', 'UTF-8') as filehandler: 
            json.dump(self.interception_index, filehandler)
            
    def build_interception_index_2(self, output_file):
        print '--------------build interception index-----------------'
        
        self.set_similar_words = dict()
        for word in self.similar_words:
            self.set_similar_words[word] = set([word_adj_simi_separator[0] for word_adj_simi_separator in self.similar_words[word]])
            
        interception_index = []
        count = 0
        
        words = [word for word in self.similar_words]
        for i in xrange(len(self.similar_words)):
            word_1 = words[i]
            interception_index.append([])
            count += 1
            if count % 10 == 0:
                print count
            for j in xrange(len(self.similar_words)):
                word_2 = words[j]
                interception_index[i].append(\
                 Separate_Anto_Syno.interception_set_index(self.set_similar_words[word_1], self.set_similar_words[word_2]))
        
        results = {Separate_Anto_Syno.LABEL: words, Separate_Anto_Syno.INTERCEPTION_INDEX:interception_index}
        with codecs.open(output_file, 'w', 'UTF-8') as filehandler: 
            json.dump(results, filehandler)
            
    def interception_index_2(self, list_similarity_1, list_similarity_2):
        sum_index = 0
        for v_1, sim_1 in list_similarity_1:
            for v_2, sim_2 in list_similarity_2:
                sum_index += self.interception_index[self.word_index_map[v_1]][self.word_index_map[v_2]] * sim_1 * sim_2
#                 sum_index += self.interception_index[self.word_index_map[v_1]][self.word_index_map[v_2]]
        return sum_index / (len(list_similarity_1) * len(list_similarity_2))
    
    def separate(self, target_word, synonym_candidates, antonym_candidates):
        self.target_word = target_word
        self.synonym_candidates = synonym_candidates
        self.antonym_candidates = antonym_candidates
        
        candidates = self.synonym_candidates + self.antonym_candidates
#         candidate_indices = [(candidate, self.interception_index_2(self.similar_words[target_word], \
#                                                                     self.similar_words[candidate])) for candidate in candidates]
        candidate_indices = [(candidate, Separate_Anto_Syno.interception_index(self.similar_words[target_word], \
                                                                    self.similar_words[candidate])) for candidate in candidates]
        candidate_indices_sorted = sorted(candidate_indices, key=lambda x : x[1])
        return candidate_indices_sorted
    
    def sort_simple(self, target_word, word_lists):
        self.target_word = target_word
        
        if target_word in self.similar_words:
            candidate_indices = [(candidate, similarity)
                                            for candidate, similarity in self.similar_words[target_word] \
                                            if candidate in word_lists]
        else :
            return []
        candidate_indices_sorted = sorted(candidate_indices, key=lambda x : x[1])
        return candidate_indices_sorted
    
    def sort(self, target_word, word_lists):
        self.target_word = target_word
        
        if target_word in self.similar_words:
            candidate_indices = [(candidate, Separate_Anto_Syno.interception_index(self.similar_words[target_word], \
                                                                        self.similar_words[candidate])) \
                                                                        for candidate in word_lists \
                                                                        if candidate in self.similar_words]
        else :
            return []
        candidate_indices_sorted = sorted(candidate_indices, key=lambda x : x[1])
        return candidate_indices_sorted

if __name__ == '__main__':
    
    axisType = ['verb', 'adj']
    
    separators = []
    for i in xrange(2):
        if axisType[i] == 'verb':
            separators.append(Separate_Anto_Syno(GOOGLE_VERB_SIMILAR_JSON))
        elif axisType[i] == 'adj':
            separators.append(Separate_Anto_Syno(GOOGLE_VERB_ADJECTIVE_SIMILAR_JSON))
        elif axisType[i] == 'adv':
            separators.append(Separate_Anto_Syno(GOOGLE_VERB_ADVERB_SIMILAR_JSON))
        elif axisType[i] == 'noun':
            separators.append(Separate_Anto_Syno(GOOGLE_VERB_NOUN_SIMILAR_JSON))
    
    target_verb = ''
    synonym_candidates = []
    middle_candidates = []
    unrelated_candidates = []
    antonym_candidates = []
    
#     '''Using verb similarity'''
#     verb_similarity_separator = Separate_Anto_Syno(TYPEDM_VERB_SIMILAR_JSON)
#     
#     '''Using verb-adjective similarity'''
#     verb_adj_simi_separator = Separate_Anto_Syno(TYPEDM_VERB_ADJECTIVE_SIMILAR_JSON)
#     
#     '''Already built'''
# #     verb_adj_simi_separator.build_interception_index_2(GOOLGE_VERB_SIMILAR_INTERCEPT_INDEX)
#     
    
    def build():
        global target_verb, synonym_candidates, middle_candidates, antonym_candidates, unrelated_candidates
        target_verb = 'build'
        synonym_candidates = ['develop', 'construct', 'erect', 'install', 'upgrade', 'fabricate', 'design', 'project', \
                               'evolve', 'cultivate', 'formulate', 'forge', 'carve', 'establish', 'assemble', 'reassemble', \
                               'organize', 'unite', 'create', 'generate', 'produce', 'expand', 'grow', 'extend', 'thrive', \
                               'widen', 'enlarge', 'enhance', 'strengthen', 'improve', 'boost', 'fortify', 'consolidate', \
                               'augment', 'accelerate', 'maintain', 'sustain', 'preserve', 'rebuild', 'incorporate', 'integrate', \
                               'redevelop']
        antonym_candidates = ['destroy', 'dismantle', 'demolish', 'raze', 'tear', 'dislodge', 'topple', 'disintegrate', \
                              'crumble', 'deconstruct', 'eliminate', 'eradicate']
         
#         unrelated_candidates = ['invest', 'allocate', 'contribute', 'sell', 'buy', 'add', 'bring', 'get', 'make',\
#                                 'manage', 'convert', 'equip', 'beautify', 'spruce']
    
    def kill():
        global target_verb, synonym_candidates, middle_candidates, antonym_candidates, unrelated_candidates
        target_verb = 'kill'
        synonym_candidates = ['slay', 'murder', 'execute', 'slaughter', 'destroy', 'massacre', 'butcher', \
                            'assassinate', 'eradicate', 'decimate', \
                            'annihilate', 'exterminate', 'extirpate', \
                            'smother', 'suffocate', 'strangle']
          
#         what_candidates += ['deaden', 'reduce', 'check', 'dull', 'diminish', 'weaken', 'cushion',\
#                             'suppress', 'blunt', 'mute', 'stifle', 'paralyse', 'numb', 'lessen',\
#                             'alleviate', 'smother', 'dampen', 'muffle', 'abate', 'quieten', 'anaesthetize', 'benumb']
          
        middle_candidates = ['injure', 'beat', 'paralyze', 'numb', 'torture', 'hit']
        antonym_candidates = ['rescue', 'save']
    
    def achieve():
        global target_verb, synonym_candidates, middle_candidates, antonym_candidates, unrelated_candidates
        target_verb = 'achieve'
        synonym_candidates = ['accomplish', 'obtain', 'succeed', 'get']
        antonym_candidates = ['fail', 'lose']
        
# #     
#     target_verb = 'buy'
#        
#     synonym_candidates = ['purchase']
#     antonym_candidates = ['sell']
    
    def reveal():
        global target_verb, synonym_candidates, middle_candidates, antonym_candidates, unrelated_candidates
        target_verb = 'reveal'
        synonym_candidates = ['disclose', 'tell', 'announce', 'publish', 'broadcast', 'leak', \
                               'communicate', 'proclaim', 'divulge', \
                               'show', 'display', 'bare', 'exhibit', \
                                'manifest', 'confirm', 'expose', 'indicate', 'explain', \
                                'publish', 'suggest', 'admit']
        antonym_candidates = ['hide', 'conceal', 'cover', 'screen', 'disguise', \
                               'obscure', 'camouflage', 'mask', 'suppress', 'veil']
        
    def grow():
        global target_verb, synonym_candidates, middle_candidates, antonym_candidates, unrelated_candidates
        target_verb = 'grow'
        synonym_candidates = ['prosper', 'develop', 'evolve', 'expand', 'burgeon', 'thrive', \
                              'climb', 'increase', 'ripen']
        antonym_candidates = ['shrink', 'wither', 'dwindle', 'deteriorate', 'stagnate']
    
    def _open():
        global target_verb, synonym_candidates, middle_candidates, antonym_candidates, unrelated_candidates
        target_verb = 'open'
        synonym_candidates = ['begin', 'commence', 'initiate', 'launch', 'start', \
                              'clear', 'crack', \
                               'undo', 'unlock', 'untie', \
                               'expand', 'spread', 'unfold', 'unroll',
                               'crack', 'rupture', 'separate', 'split',
                               'disclose', 'divulge', 'exhibit', 'explain', 'show'    ]
        antonym_candidates = ['close', 'conclude', 'end', 'finish', 'terminate', \
                              'block', 'close', 'fasten', 'lock', 'obstruct', 'seal', 'shut', 'fold'  ]
       
    
    def create_graph():
        global target_verb, synonym_candidates, middle_candidates, antonym_candidates, unrelated_candidates
        global separators
        l_1 = separators[0].sort(target_verb, synonym_candidates + middle_candidates\
                                              + antonym_candidates + unrelated_candidates)
        l_2 = separators[1].sort(target_verb, synonym_candidates + middle_candidates\
                                              + antonym_candidates + unrelated_candidates)
        print l_1
        print l_2
        l_val_1 = dict()
        l_val_2 = dict()
           
        for word, value in l_1:
            l_val_1[word] = value
        for word, value in l_2:
            l_val_2[word] = value
                  
        fig = plt.figure()
        colors = ['b', 'y', 'r', 'g']
              
        ax = fig.add_subplot(1, 1, 1)
    #     v = 0.1
    #     a = 0.1
    #     for word in synonym_candidates:
    #         v += a
    #         ax.scatter(l_val_1[word],l_val_2[word], color = colors[0])
    #         ax.text(l_val_1[word],l_val_2[word], word)
    #         
    #     v = 0.1
    #     for word in antonym_candidates:
    #         v += a
    #         ax.scatter(l_val_1[word],l_val_2[word], color = colors[1])
    #         ax.text(l_val_1[word],l_val_2[word], word)
             
        word_lists = [synonym_candidates, middle_candidates, antonym_candidates, unrelated_candidates]
        for i in xrange(len(word_lists)):
            word_list = word_lists[i]
            for word in word_list:
                ax.scatter(l_val_1[word], l_val_2[word], color=colors[i])
                ax.text(l_val_1[word], l_val_2[word], word)
              
        plt.xlabel('Similarity using ' + axisType[0] + ' to ' + target_verb)
        plt.ylabel('Similarity using ' + axisType[1] + ' to ' + target_verb)
        plt.show()
        
    achieve()
    
    create_graph()
