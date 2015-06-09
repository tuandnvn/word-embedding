'''
Created on Jun 8, 2015

@author: Tuan Do
'''
import codecs
import glob
import json
import os
import pprint

from cpa.prototype import TRAIN, TEST

from create_seed_vectors import DEPENDENCY, TOKENS, COREFERENCE, TREE, TEXT


def get_parsed_from_file (file_name):
    with codecs.open(file_name, 'r', 'utf-8') as file_handler:
        tokens = []
        sent_tokens = []
        dependencies = []
        sent_dependencies = []
        
        for line in file_handler:
            if line.strip() == '':
                tokens.append(sent_tokens)
                
                '''Recover word in dependency'''
                for dependency in sent_dependencies:
                    if int(dependency[3]) == 0:
                        dependency[1] = 'ROOT'
                    else:
                        dependency[1] = sent_tokens[int(dependency[3]) - 1][0]
                dependencies.append(sent_dependencies)
                sent_tokens = []
                sent_dependencies = []
            else:
                '''1    The    the    DT    _    3    det    O'''
                '''6    Center    center    NNP    _    4    pobj    I-ORG'''
                no, original, lem, pos, pos_2, head_no, dep_type, ne_type = line.split()
                '''[u'The', u'0', u'3', u'the', u'DT', u'O']'''
                if ne_type == 'O':
                    ne_type_process = u'O'
                else:
                    ne_type_process = ne_type.split('-')[1]
                token = [original, '', '', lem, pos, ne_type_process]
                
                '''[u'root', u'ROOT', u'contained', u'0', u'4']
                [u'det', u'manifesto', u'The', u'3', u'1']'''
                dependency = [dep_type, None, original, head_no, no]
                
                sent_tokens.append(token)
                sent_dependencies.append(dependency)
        
        text = []
        for sent_tokens in tokens:
            text.append(' '.join([token[0] for token in sent_tokens]))
        return {COREFERENCE: [], TREE: [], TOKENS: tokens, DEPENDENCY: dependencies, TEXT: text}
                
def get_parsed_from_dir(directory, output_file):
    data = {}
    for training_type in [TRAIN, TEST]:
        cnlp_files = glob.glob(os.path.join(directory, training_type, '*.cnlp'))
        data[training_type] = {}
        for cnlp_file in cnlp_files:
            rel_name = cnlp_file.split(os.path.sep)[-1]
            key_name = rel_name.split('.')[0]
            json_data = get_parsed_from_file(cnlp_file)
            data[training_type][key_name] = json_data
    with codecs.open(output_file, 'w', 'utf-8') as file_handler:
        json.dump(data, file_handler)
        
if __name__ == '__main__':
#     pprint.pprint( get_parsed_from_file('sample-line.txt.cnlp'))
    get_parsed_from_dir('clearnlp_dep', 'output_file.json')