'''
Created on Apr 29, 2015

@author: User
'''
import codecs
import logging
import os

from gensim import utils
import gensim
import numpy

from run_embed import PmiModel, raw2ppmi

logger = logging.getLogger("test")

def calculate_category_pmi(dense_vectors, word2id, category_name, list_of_pairs):
    """
    For a list of pairs of words that sharing a same semantic-syntactic relation,
    calculate the average ppmi of all the pairs 
    """
    print category_name
    logger.info("Calculate pmi of category %s" % category_name)
    cat_sum = 0.0
    count = 0
    for pair in list_of_pairs:
        word_1, word_2 = pair
        if word_1.lower() in word2id and word_2.lower() in word2id:
            id_1 = word2id[word_1.lower()]
            id_2 = word2id[word_2.lower()]
            cat_sum += dense_vectors[id_1, id_2]
            count += 1
    
    cat_average = cat_sum / count
    print cat_average
    print 100 * count / len(list_of_pairs)
    
def calculate_pmi(dense_vectors, word2id, input_file):
    with codecs.open(input_file, 'r', 'utf-8') as file_handler:
        current_relation = None
        relations = {}
        for line in file_handler:
            if line.strip()[:1] == ':':
                current_relation = line.strip()[1:].strip()
                relations[current_relation] = []
            else:
                relations[current_relation].append(tuple(line.strip().split()))
        
        for relation in relations:
            calculate_category_pmi(dense_vectors, word2id, relation, relations[relation])
    
if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s : %(threadName)s : %(levelname)s : %(message)s', level=logging.INFO)
    outf = lambda prefix: os.path.join('output', prefix)
    
    word2id = utils.unpickle(outf('word2id-30k-filter'))
    
    if os.path.exists(outf('cooccur.npy')):
        logger.info("raw cooccurrence matrix found, loading")
        raw = numpy.load(outf('cooccur.npy'))
    # store the SPPMI matrix in sparse Matrix Market format on disk
    gensim.corpora.MmCorpus.serialize(outf('pmi_matrix.mm'), raw2ppmi(raw, word2id, k_shift=1))
    
    model = PmiModel(gensim.corpora.MmCorpus(outf('pmi_matrix.mm-noshift')))
    
    dv = model.word_vectors.todense()
    
    calculate_pmi(dv, word2id, )
