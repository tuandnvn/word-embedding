#!/usr/bin/env cython
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True
# coding: utf-8
#
# Copyright (C) 2013 Radim Rehurek <me@radimrehurek.com>
# Licensed under the GNU LGPL v2.1 - http://www.gnu.org/licenses/lgpl.html

import cython
import numpy as np
cimport numpy as np

from libc.math cimport exp
from libc.string cimport memset

cdef extern from "voidptr.h":
    void* PyCObject_AsVoidPtr(object obj)

from scipy.linalg.blas import fblas

REAL = np.float32
ctypedef np.float32_t REAL_t

DEF MAX_SENTENCE_LEN = 10000

ctypedef void (*scopy_ptr) (const int *N, const float *X, const int *incX, float *Y, const int *incY) nogil
ctypedef void (*saxpy_ptr) (const int *N, const float *alpha, const float *X, const int *incX, float *Y, const int *incY) nogil
ctypedef float (*sdot_ptr) (const int *N, const float *X, const int *incX, const float *Y, const int *incY) nogil
ctypedef double (*dsdot_ptr) (const int *N, const float *X, const int *incX, const float *Y, const int *incY) nogil
ctypedef double (*snrm2_ptr) (const int *N, const float *X, const int *incX) nogil
ctypedef void (*sscal_ptr) (const int *N, const float *alpha, const float *X, const int *incX) nogil

# ctypedef unsigned long long (*fast_sentence_sg_neg_ptr) (
#     const int negative, np.uint32_t *table, unsigned long long table_len,
#     REAL_t *syn0, REAL_t *syn1neg, const int size, const np.uint32_t word_index,
#     const np.uint32_t word2_index, const REAL_t alpha, REAL_t *work,
#     unsigned long long next_random) nogil

cdef scopy_ptr scopy=<scopy_ptr>PyCObject_AsVoidPtr(fblas.scopy._cpointer)  # y = x
cdef saxpy_ptr saxpy=<saxpy_ptr>PyCObject_AsVoidPtr(fblas.saxpy._cpointer)  # y += alpha * x
cdef sdot_ptr sdot=<sdot_ptr>PyCObject_AsVoidPtr(fblas.sdot._cpointer)  # float = dot(x, y)
cdef dsdot_ptr dsdot=<dsdot_ptr>PyCObject_AsVoidPtr(fblas.sdot._cpointer)  # double = dot(x, y)
cdef snrm2_ptr snrm2=<snrm2_ptr>PyCObject_AsVoidPtr(fblas.snrm2._cpointer)  # sqrt(x^2)
cdef sscal_ptr sscal=<sscal_ptr>PyCObject_AsVoidPtr(fblas.sscal._cpointer) # x = alpha * x
# cdef fast_sentence_sg_neg_ptr fast_sentence_sg_neg

DEF EXP_TABLE_SIZE = 1000
DEF MAX_EXP = 6

cdef REAL_t[EXP_TABLE_SIZE] EXP_TABLE

cdef int ONE = 1
cdef REAL_t ONEF = <REAL_t>1.0

cdef unsigned long long fast_sentence1_sg_neg(
    const int negative, np.uint32_t *table, unsigned long long table_len,
    REAL_t *syn0, REAL_t *syn1neg, const int size, const np.uint32_t word_index,
    const np.uint32_t word2_index, const REAL_t alpha, REAL_t *work,
    unsigned long long next_random, REAL_t * prototype, const np.uint32_t before) nogil:

    cdef long long a
    cdef long long row1 = word2_index * size, row2
    cdef unsigned long long modulo = 281474976710655ULL
    cdef REAL_t f, g, label
    cdef np.uint32_t target_index
    cdef int d
    cdef int halfsize = size / 2

    memset(work, 0, size * cython.sizeof(REAL_t))

    for d in range(negative+1):
        if d == 0:
            target_index = word_index
            label = ONEF
        else:
            target_index = table[(next_random >> 16) % table_len]
            next_random = (next_random * <unsigned long long>25214903917ULL + 11) & modulo
            if target_index == word_index:
                continue
            label = <REAL_t>0.0
 
        row2 = target_index * size
         
        if before :
            f = <REAL_t>sdot(&halfsize, &prototype[halfsize], &ONE, &syn1neg[row2], &ONE)
        else:
            f = <REAL_t>sdot(&halfsize, prototype, &ONE, &syn1neg[row2 + halfsize], &ONE)
             
        if f <= -MAX_EXP or f >= MAX_EXP:
            continue
        f = EXP_TABLE[<int>((f + MAX_EXP) * (EXP_TABLE_SIZE / MAX_EXP / 2))]
        g = (label - f) * alpha
        
        if before :
            saxpy(&halfsize, &g, &syn1neg[row2], &ONE, work, &ONE)
        else:
            saxpy(&halfsize, &g, &syn1neg[row2 + halfsize], &ONE, work, &ONE)
             
    if before :
        saxpy(&halfsize, &ONEF, work, &ONE, &prototype[halfsize], &ONE)
    else:
        saxpy(&halfsize, &ONEF, work, &ONE, prototype, &ONE)

    return next_random

def train_sentence_sg(model, sentence, alpha, _work, _target_index, _window, _syn0_proto, _syn1neg_proto) :
    cdef int hs = model.hs
    cdef int negative = model.negative

    cdef REAL_t *syn0 = <REAL_t *>(np.PyArray_DATA(model.syn0))
    cdef REAL_t *syn0_proto = <REAL_t *>(np.PyArray_DATA(_syn0_proto))
    cdef REAL_t *syn1neg_proto = <REAL_t *>(np.PyArray_DATA(_syn1neg_proto))
    cdef REAL_t *work
    cdef REAL_t _alpha = alpha
    cdef int target_index = _target_index
    cdef int size = model.layer1_size

    cdef int codelens[MAX_SENTENCE_LEN]
    cdef np.uint32_t indexes[MAX_SENTENCE_LEN]
    cdef np.uint32_t reduced_windows[MAX_SENTENCE_LEN]
    cdef int sentence_len
    cdef int window = _window

    cdef int i, j, k
    cdef long result = 0

    # For negative sampling
    cdef REAL_t *syn1neg
    cdef np.uint32_t *table
    cdef unsigned long long table_len
    cdef unsigned long long next_random

    syn1neg = <REAL_t *>(np.PyArray_DATA(model.syn1neg))
    table = <np.uint32_t *>(np.PyArray_DATA(model.table))
    table_len = len(model.table)
    next_random = (2**24) * np.random.randint(0, 2**24) + np.random.randint(0, 2**24)

    # convert Python structures to primitive types, so we can release the GIL
    work = <REAL_t *>np.PyArray_DATA(_work)
    sentence_len = <int>min(MAX_SENTENCE_LEN, len(sentence))
    
    cdef int before

    for i in range(sentence_len):
        word = sentence[i]
        if word is None:
            codelens[i] = 0
        else:
            indexes[i] = word.index
            codelens[i] = 1
            result += 1

    # release GIL & train on the sentence
    with nogil:
        if codelens[target_index] != 0:
            j = target_index - window
            if j < 0:
                j = 0
            k = target_index + window + 1 
            if k > sentence_len:
                k = sentence_len
            for j in range(j, k):
                if j == target_index or codelens[j] == 0:
                    continue
                if j < target_index:
                    before = 1
                else:
                    before = 0
                next_random = fast_sentence1_sg_neg(negative, table, table_len, syn0, syn1neg, size, indexes[j], indexes[target_index], _alpha, work, next_random, syn0_proto, before)

    return result

def init():
    """
    Precompute function `sigmoid(x) = 1 / (1 + exp(-x))`, for x values discretized
    into table EXP_TABLE.

    """
    global fast_sentence_sg_neg

    cdef int i
    cdef float *x = [<float>10.0]
    cdef float *y = [<float>0.01]
    cdef float expected = <float>0.1
    cdef int size = 1
    cdef double d_res
    cdef float *p_res

    # build the sigmoid table
    for i in range(EXP_TABLE_SIZE):
        EXP_TABLE[i] = <REAL_t>exp((i / <REAL_t>EXP_TABLE_SIZE * 2 - 1) * MAX_EXP)
        EXP_TABLE[i] = <REAL_t>(EXP_TABLE[i] / (EXP_TABLE[i] + 1))

    # check whether sdot returns double or float
    d_res = dsdot(&size, x, &ONE, y, &ONE)
    p_res = <float *>&d_res
    
    if (abs(d_res - expected) < 0.0001):
#         fast_sentence_sg_neg = fast_sentence1_sg_neg
        return 0  # double
    elif (abs(p_res[0] - expected) < 0.0001):
#         fast_sentence_sg_neg = fast_sentence1_sg_neg
        return 1  # float
    else:
        # neither => use cython loops, no BLAS
        # actually, the BLAS is so messed up we'll probably have segfaulted above and never even reach here
#         fast_sentence_sg_neg = fast_sentence1_sg_neg
        return 2

FAST_VERSION = init()  # initialize the module
