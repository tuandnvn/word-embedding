'''
Created on Mar 11, 2015

@author: Tuan Do
'''
import codecs
import json

from util import GOOGLE_VERB_SIMILAR_JSON, GOOGLE_VERB_NOUN_SIMILAR_JSON
from cluster.method.hierarchical import HierarchicalClustering
from cluster.method.kmeans import KMeansClustering
from relativeGraph.build_independent_graph import BuildIndependentGraph
from separate_anto_syno import Separate_Anto_Syno


class JaccardDistanceAmongAll(BuildIndependentGraph):
    '''
    classdocs
    '''


    def __init__(self, similar_file):
        '''
        Constructor
        '''
        '''
        Constructor
        '''
        with codecs.open(similar_file, 'r', 'UTF-8') as filehandler: 
            self.original_similar_words = json.load(filehandler)
        print '------Done load similar_file------'
        
        self.original_similar_index = dict()
        for word_1 in self.original_similar_words:
            for word_2, similarity in self.original_similar_words[word_1]:
                self.original_similar_index[(word_1, word_2)] = similarity
        print '------Done build similar index------'
        
        
    def build_graph_with_jaccard(self, target_word, word_list):
        self.similar_words = dict()
        self.similar_index = dict()
        
        word_list_include_target_word = [target_word] + word_list
        for i in xrange(len(word_list_include_target_word)):
            word_1 = word_list_include_target_word[i]
            self.similar_words[word_1] = [(word_2, Separate_Anto_Syno.interception_index(\
                                                        self.original_similar_words[word_1], \
                                                        self.original_similar_words[word_2])) \
                                          for word_2 in word_list_include_target_word if word_2 != word_1]
        
        for word_1 in self.similar_words:
            for word_2, similarity in self.similar_words[word_1]:
                self.similar_index[(word_1, word_2)] = similarity
        
        return self.build_graph(target_word)
    
if __name__ == '__main__':
#     t = JaccardDistanceAmongAll(GOOGLE_VERB_SIMILAR_JSON)
    t = JaccardDistanceAmongAll(GOOGLE_VERB_NOUN_SIMILAR_JSON)
    
    target_verb = 'build'
    synonym_candidates = ['develop', 'construct', 'erect', 'install', 'upgrade', 'fabricate', 'design', 'project', \
                           'evolve', 'cultivate', 'formulate', 'forge', 'carve', 'establish', 'assemble', 'reassemble', \
                           'organize', 'unite', 'create', 'generate', 'produce', 'expand', 'grow', 'extend', 'thrive', \
                           'widen', 'enlarge', 'enhance', 'strengthen', 'improve', 'boost', 'fortify', 'consolidate', \
                           'augment', 'accelerate', 'maintain', 'sustain', 'preserve', 'rebuild', 'incorporate', 'integrate', \
                           'redevelop']
    antonym_candidates = ['destroy', 'dismantle', 'demolish', 'raze', 'tear', 'dislodge', 'topple', 'disintegrate', \
                          'crumble', 'deconstruct', 'eliminate', 'eradicate']
    
    unrelated_candidates = ['invest', 'allocate', 'contribute', 'sell', 'buy', 'add', 'bring', 'get', 'make',\
                            'manage', 'convert', 'equip', 'beautify', 'spruce']
    
    g = t.build_graph_with_jaccard(target_verb, synonym_candidates + antonym_candidates + unrelated_candidates)
    g.save_to_gdf(target_verb + '_type2.gdf')
    
    word_list = [target_verb] + synonym_candidates + antonym_candidates + unrelated_candidates
    
    u = HierarchicalClustering(word_list, lambda word_1, word_2: 1 - Separate_Anto_Syno.interception_index(\
                                                                    t.original_similar_words[word_1], \
                                                                    t.original_similar_words[word_2]), \
                               linkage = 'uclus')
    start = 0.8
    step = 0.025
    for i in xrange(8):
        print '----------------------------------------'
        print start + step * i
        clusters = u.getlevel( start + step * i)
        for cluster in clusters:
            print cluster
            