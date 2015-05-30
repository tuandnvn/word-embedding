'''
This module create seed vector for proposal-6
Finding pattern-vectors for Pdev pattern
'''
import os

from utils import DATA_DIR, GOOGLE_DIR

REMOVING_STRS = ['_', '(', ')', 'or', '|', '[', ']', '{', '}', '1', '2', '3', 'NO OBJ']

TRAIN = 'train'
TEST = 'test'
PDEV_DIR = os.path.join(DATA_DIR, "pdev")
PATTERN_FILE = os.path.join(PDEV_DIR, "corpus.json")
'''With longer context has been added'''
PATTERN_FILE_EXTEND = os.path.join(PDEV_DIR, "corpus_extend.json")
PATTERN_PICKLE_FILE = os.path.join(PDEV_DIR, "pattern.pkl")
PATTERN_SPLIT_FILE = os.path.join(PDEV_DIR, "corpus_split.json")
PATTERN_SPLIT_FILE_EXTEND = os.path.join(PDEV_DIR, "corpus_extend_split.json")
WORD2VEC_POS_OLD = os.path.join(GOOGLE_DIR,'trunk', 'word2vec_pos.mo')
WORD2VEC_POS_MODEL = os.path.join(GOOGLE_DIR, 'trunk', 'w2v_all_pos_f_200000')
WORD2VEC_POS = os.path.join(GOOGLE_DIR, 'trunk', 'word2vec_all_pos_f_200000.mo')
WORD2VEC_VOCAB = os.path.join(GOOGLE_DIR, 'trunk', 'vocab_all.f_300k.txt')
WORD2VEC_POS_BF = os.path.join(GOOGLE_DIR, 'trunk', 'word2vec_bf_all_pos_f_200000.mo')
WORD2VEC_POS_BF_50K = os.path.join(GOOGLE_DIR, 'trunk', 'word2vec_bf_50000_pos_f_200000.mo')
WORD2VEC_POS_INCOR_50K = os.path.join(GOOGLE_DIR, 'trunk', 'word2vec_incor_50000_pos_f_200000.mo')
WORD2VEC_POS_INCOR = os.path.join(GOOGLE_DIR, 'trunk', 'word2vec_incor_all_pos_f_200000.mo')

PROTOTYPE_POS_BF = os.path.join(PDEV_DIR, 'prototype.pos.bf.json')
PROTOTYPE_POS_BF_AFTER_RETRAIN = os.path.join(PDEV_DIR, 'prototype.out.pos.bf.json')
PROTOTYPE_POS = os.path.join(PDEV_DIR, 'prototype.pos.json')
PROTOTYPE_POS_AFTER_RETRAIN = os.path.join(PDEV_DIR, 'prototype.out.pos.json')

SEED_VECTOR_FILE = os.path.join(PDEV_DIR, 'seed_vector.obj')
SEED_VECTOR_2_FILE = os.path.join(PDEV_DIR, 'seed_vector_2.obj')
SEED_VECTOR_FILE_BF = os.path.join(PDEV_DIR, 'seed_vector_bf.obj')
SEED_VECTOR_FILE_EXTEND = os.path.join(PDEV_DIR, 'seed_vector_extend.obj')
SEED_VECTOR_2_FILE_EXTEND = os.path.join(PDEV_DIR, 'seed_vector_2_extend.obj')