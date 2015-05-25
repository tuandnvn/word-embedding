'''
Created on Mar 31, 2015

@author: User
'''
import codecs
import glob
import itertools
import json
import logging
import os

from gensim import utils
import gensim

from src.word2vec_bf_retrain import Word2Vec_BF_Retrain
from test_glove import  accuracy


DOC_LIMIT = 50000

logger = logging.getLogger("test")

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s : %(threadName)s : %(levelname)s : %(message)s', level=logging.INFO)
    
    q_file = os.path.join('output', 'questions-words.txt')
    outf = lambda prefix: os.path.join('output', prefix)
    
    SELECTION = 'pos'
    FILE_SIZE = 'all'
    TOKEN_LIMIT = 200000
    
#     if SELECTION == 'pos':
#         input_file = outf( 'title_tokens_%s_pos.txt.gz' % FILE_SIZE)
#         id2word_files = glob.glob(outf('id2word_all_pos_filter_*'))
#         if len(id2word_files) > 0:
#             id2word_all = id2word_files[0]
#         word2id_file = outf('word2id_%s_pos_filter_%s' % (FILE_SIZE, TOKEN_LIMIT))
#         original_word2vec_model_file = outf('w2v_bf_%s_pos_f_%s' % (FILE_SIZE, TOKEN_LIMIT))
#         word2vec_model_file = outf('w2v_bf_retrain_%s_pos_f_%s' % (FILE_SIZE, TOKEN_LIMIT))
#         prototype_file = outf('prototype.pos.bf.json')
#         output_prototype_file = outf('prototype.out.pos.bf.json')
#         using_pos = True
#     elif SELECTION == 'normal':
#         input_file = outf('title_tokens_%s.txt.gz' % FILE_SIZE)
#         id2word_files = glob.glob(outf('id2word_all_filter_*'))
#         if len(id2word_files) > 0:
#             id2word_all = id2word_files[0]
#         word2id_file = outf('word2id_%s_filter_%s' % (FILE_SIZE, TOKEN_LIMIT))
#         original_word2vec_model_file = outf('w2v_bf_%s_f_%s' % (FILE_SIZE, TOKEN_LIMIT))
#         word2vec_model_file = outf('w2v_bf_retrain_%s_f_%s' % (FILE_SIZE, TOKEN_LIMIT))
#         prototype_file = outf('prototype.bf.json')
#         output_prototype_file = outf('prototype.out.bf.json')
#         using_pos = False
    
    BNC_FILE_SIZE = '1000'
    id2word_all = None
    input_file = outf( 'bnc_%s.txt.gz' % BNC_FILE_SIZE)
    word2id_file = outf('word2id_bnc_%s' % (BNC_FILE_SIZE))
    original_word2vec_model_file = outf('w2v_bf_%s_pos_f_%s' % (FILE_SIZE, TOKEN_LIMIT))
    word2vec_model_file = outf('w2v_bf_retrain_bnc_%s_pos_f_%s' % (BNC_FILE_SIZE, TOKEN_LIMIT))
    prototype_file = outf('prototype.pos.bf.json')
    output_prototype_file = outf('prototype.out.pos.bf.json')
    using_pos = True
            
    in_file = gensim.models.word2vec.LineSentence(input_file)
    sentences = lambda: itertools.islice(in_file, DOC_LIMIT)
    
    with codecs.open(prototype_file, 'r', 'utf-8') as file_handler:
        prototype = json.load(file_handler)

    if os.path.exists(word2id_file):
        print 'Load dictionary'
        word2id = utils.unpickle(word2id_file)
    else:
        print 'Build dictionary'
        if id2word_all != None:
            print 'id2word file ' + id2word_all + ' found. Load'
            id2word = gensim.corpora.Dictionary.load(id2word_all)
        else:
            print 'id2word not found. Build the dictionary'
            id2word = gensim.corpora.Dictionary(sentences(), prune_at=1000000)
        id2word.filter_extremes(keep_n=TOKEN_LIMIT, no_above = 1, no_below = 10)  # filter out too freq/infreq words
        word2id = dict((v, k) for k, v in id2word.iteritems())
        utils.pickle(word2id, word2id_file)
        
     
    if os.path.exists(word2vec_model_file):
        print 'Load word2vec bf model'
        model = utils.unpickle(word2vec_model_file)
    else:
        print 'Build word2vec bf model'
        corpus = lambda: ([word for word in sentence if word in word2id] for sentence in sentences())
        initial_model = utils.unpickle(original_word2vec_model_file)
        model = Word2Vec_BF_Retrain( initial_model, prototype, size=300, min_count=0, window=5, workers=8, negative=5, iter=1)
        model.train(corpus())  # train with 1 epoch
        model.init_sims(replace=True)
        model.word2id = dict((w, v.index) for w, v in model.vocab.iteritems())
        model.id2word = utils.revdict(model.word2id)
        model.word_vectors = model.syn0norm
        model.update_prototype_to_current()
        model.save_prototype_text('2.txt')
        model.save_prototype(output_prototype_file)
#         utils.pickle(model, word2vec_model_file)
