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
PATTERN_SPLIT_FILE = os.path.join(PDEV_DIR, "corpus_split.json")
WORD2VEC_POS = os.path.join(GOOGLE_DIR,'trunk', 'word2vec_pos.mo')
WORD2VEC_POS_FRE = os.path.join(GOOGLE_DIR, 'trunk', 'word2vec_all_pos_f_200000.mo')
WORD2VEC_POS_BF = os.path.join(GOOGLE_DIR, 'trunk', 'word2vec_bf_all_pos_f_200000.mo')

PROTOTYPE_POS_BF = os.path.join(PDEV_DIR, 'prototype.pos.bf.json')
PROTOTYPE_POS_BF_AFTER_RETRAIN = os.path.join(PDEV_DIR, 'prototype.out.pos.bf.json')
PROTOTYPE_POS = os.path.join(PDEV_DIR, 'prototype.pos.json')

SEED_VECTOR_2_FILE = os.path.join(PDEV_DIR, 'seed_vector_2.obj')