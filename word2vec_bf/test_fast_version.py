'''
Created on May 15, 2015

@author: Tuan Do
'''
import os

import gensim
from gensim.models.word2vec_inner import FAST_VERSION


print os.path.dirname(gensim.models.__file__)
print FAST_VERSION
