import glob
import itertools
import logging
import os
import sys

from gensim import matutils, utils
import gensim
import numpy

import pyximport; pyximport.install(setup_args={'include_dirs': numpy.get_include()})

logger = logging.getLogger("run_embed")

DOC_LIMIT = None
TOKEN_LIMIT = 20000
WORKERS = 8
WINDOW = 3
DYNAMIC_WINDOW = False
FILE_SIZE = 'all'
posi = True
model = None

def    raw2ppmi(cooccur):
    """
    Convert raw counts from `get_coccur` into positive PMI values (as per Levy & Goldberg),
    in place.

    The result is an efficient stream of sparse word vectors (=no extra data copy).

    """
    logger.info("computing PPMI on co-occurence counts")

    # following lines a bit tedious, as we try to avoid making temporary copies of the (large) `cooccur` matrix
    marginal_word = cooccur.sum(axis=1)
    marginal_context = cooccur.sum(axis=0)
    numpy.seterr(divide='ignore', invalid = 'ignore')
    
    cooccur /= marginal_word[:, None]
    cooccur[marginal_word == 0, :] = 0
    
    cooccur /= marginal_context  # #(w, c) / (#w * #c)
    cooccur[:, marginal_context == 0] = 0
    
    cooccur *= marginal_word.sum()  # #(w, c) * D / (#w * #c)
    numpy.log(cooccur, out=cooccur)  # PMI = log(#(w, c) * D / (#w * #c))

    logger.info("clipping PMI scores to be non-negative PPMI")
    cooccur.clip(0.0, out=cooccur)  # SPPMI = max(0, log(#(w, c) * D / (#w * #c)) - log(k))

    logger.info("normalizing PPMI word vectors to unit length")
    for i, vec in enumerate(cooccur):
        cooccur[i] = matutils.unitvec(vec)

    return matutils.Dense2Corpus(cooccur, documents_columns=False)

class PmiModel(object):
    def __init__(self, corpus):
        # serialize PPMI vectors into an explicit sparse CSR matrix, in RAM, so we can do
        # dot products more easily
        self.word_vectors = matutils.corpus2csc(corpus).T
        
if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s : %(threadName)s : %(levelname)s : %(message)s', level=logging.INFO)
    logger.info("running %s" % " ".join(sys.argv))

    # check and process cmdline input
    outf = lambda prefix: os.path.join('output', prefix)
    logger.info("output file template will be %s" % outf('PREFIX'))

    input_file = outf( 'title_tokens_%s.txt.gz' % FILE_SIZE)
    
    id2word_files = glob.glob(outf('id2word_all_filter_*'))
    if len(id2word_files) > 0:
        id2word_all = id2word_files[0]
    word2id_file = outf('word2id_%s_filter_%s' % (FILE_SIZE, TOKEN_LIMIT))
    
    if posi:
        pmi_model_file = 'pmi_posi.%s.f_%s.w_%s' % (FILE_SIZE, TOKEN_LIMIT, WINDOW)
        pmi_matrix_file = 'pmi_matrix_posi.%s.f_%s.w_%s.mm' % (FILE_SIZE, TOKEN_LIMIT, WINDOW)
        cooccur_file = 'cooccur_posi.%s.f_%s.w_%s.npy' % (FILE_SIZE, TOKEN_LIMIT, WINDOW)
        from cooccur_matrix_posi import get_cooccur
    else:
        pmi_model_file = 'pmi.%s.f_%s.w_%s' % (FILE_SIZE, TOKEN_LIMIT, WINDOW)
        pmi_matrix_file = 'pmi_matrix.%s.f_%s.w_%s.mm' % (FILE_SIZE, TOKEN_LIMIT, WINDOW)
        cooccur_file = 'cooccur.%s.f_%s.w_%s.npy' % (FILE_SIZE, TOKEN_LIMIT, WINDOW)
        from cooccur_matrix import get_cooccur
    
    in_file = gensim.models.word2vec.LineSentence(input_file)
    sentences = lambda: itertools.islice(in_file, DOC_LIMIT)
    
    if os.path.exists(word2id_file):
        print 'Load dictionary'
        word2id = utils.unpickle(word2id_file)
        id2word = dict((v, k) for k, v in word2id.iteritems())
    else:
        print 'Build dictionary'
        if id2word_all != None:
            print 'id2word file ' + id2word_all + ' found. Load'
            id2word = gensim.corpora.Dictionary.load(id2word_all)
        else:
            print 'id2word not found. Build the dictionary'
            id2word = gensim.corpora.Dictionary(sentences(), prune_at=1000000)
        id2word.filter_extremes(keep_n=TOKEN_LIMIT)  # filter out too freq/infreq words
        word2id = dict((v, k) for k, v in id2word.iteritems())
        utils.pickle(word2id, word2id_file)
    
    corpus = lambda: ([word for word in sentence if word in word2id] for sentence in sentences())
    
    if os.path.exists(outf(pmi_model_file)):
        logger.info("PMI model found, loading")
        model = utils.unpickle(outf(pmi_model_file))
    else:
        if not os.path.exists(outf(pmi_matrix_file)):
            logger.info("PMI matrix not found, creating")
            if os.path.exists(outf(cooccur_file)):
                logger.info("raw cooccurrence matrix found, loading")
                raw = numpy.load(outf(cooccur_file))
            else:
                logger.info("raw cooccurrence matrix not found, creating")
                raw = get_cooccur(corpus(), word2id, window=WINDOW, dynamic_window=False)
                numpy.save(outf(cooccur_file), raw)
            # store the SPPMI matrix in sparse Matrix Market format on disk
            gensim.corpora.MmCorpus.serialize(outf(pmi_matrix_file), raw2ppmi(raw))
            del raw
        logger.info("PMI model not found, creating")
        model = PmiModel(gensim.corpora.MmCorpus(outf(pmi_matrix_file)))
        model.word2id = word2id
        model.id2word = id2word
        utils.pickle(model, outf(pmi_model_file))
        
# c = 0
# for t in ppmi:
#     if c > 0:
#         print t
# #     print numpy.linalg.norm([x[1] for x in t])
#     c += 1
#     if c > 1:
#         break