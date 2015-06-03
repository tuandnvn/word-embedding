'''
Created on Mar 12, 2015

@author: Tuan Do
'''
import codecs

from util import ADVERBS


words = []
with codecs.open(ADVERBS, 'r', 'UTF-8') as filehandler:
    for line in filehandler:
        words.append(line.strip().split()[0])
  
with codecs.open(ADVERBS, 'w', 'UTF-8') as filehandler:
    for word in words:
        if word.endswith('ly'):
            filehandler.write(word)
            filehandler.write('\n')