'''
Created on Apr 28, 2015

@author: Tuan Do
'''
import codecs

from util import ADDTIONAL_RELATION, ADDTIONAL_ANALOGY_QUESTION_FILE

class AnalogyCreator(object):
    '''
    classdocs
    '''


    def __init__(self, original_pair_file, analogy_question_file):
        '''
        Constructor
        '''
        self.relations = {}
        with codecs.open(original_pair_file, 'r', 'utf-8') as file_handler:
            current_relation = None
            for line in file_handler:
                if line.strip()[:1] == ':':
                    current_relation = line.strip()[1:].strip()
                    self.relations[current_relation] = []
                else:
                    self.relations[current_relation].append(line.strip().split())
                    
        self.write_analogy_file(analogy_question_file)
        
    def write_analogy_file(self, analogy_question_file):
        with codecs.open(analogy_question_file, 'w', 'utf-8') as file_handler:
            for relation in self.relations:
                file_handler.write(': ' + relation + '\n')
                list_of_pairs = self.relations[relation]
                for i, pair_1 in enumerate(list_of_pairs):
                    for j, pair_2 in enumerate(list_of_pairs):
                        if i != j:
                            file_handler.write(' '.join(pair_1) + ' ' + ' '.join(pair_2) + '\n')
                for i, pair_1 in enumerate(list_of_pairs):
                    for j, pair_2 in enumerate(list_of_pairs):
                        if i != j:
                            if relation[:len('antonym')] == 'antonym':
                                file_handler.write(' '.join(pair_1[::-1]) + ' ' + ' '.join(pair_2) + '\n')

if __name__ == '__main__':
    t =    AnalogyCreator(ADDTIONAL_RELATION, ADDTIONAL_ANALOGY_QUESTION_FILE)