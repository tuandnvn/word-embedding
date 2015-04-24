'''
Created on Mar 7, 2015

@author: Tuan Do
'''
import codecs
import operator
from os import listdir

import matplotlib
from numpy import *
from numpy import linalg as la
from numpy.linalg import *

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


label_file = 'kill.txt'
# load data points
raw_data = loadtxt(label_file + '.dat', delimiter=',')

labels = []
with codecs.open(label_file, 'r', 'UTF-8') as file_handler:
    for line in file_handler:
        labels.append(line.strip())
samples, features = shape(raw_data)

print samples
print features

# normalize and remove mean
data = mat(raw_data[:, 1:])
 
def svd(data, S=2):
     
    # calculate SVD
    U, s, V = linalg.svd(data)
    Sig = mat(eye(S) * s[:S])
    # tak out columns you don'verb_adj_simi_separator need
    newdata = U[:, :S]
     
    # this line is used to retrieve dataset 
    # ~ new = U[:,:2]*Sig*V[:2,:]
    print '----------------------------'
    print s
    
    verb_adj_simi_separator = 0
    for i in xrange(len(s)):
        verb_adj_simi_separator += s[i] * s[i]
    print verb_adj_simi_separator
    verb_adj_simi_separator = 0
    for i in xrange(3):
        verb_adj_simi_separator += s[i] * s[i]
    print verb_adj_simi_separator
    
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1, projection='3d')
#     ax = fig.add_subplot(1, 1, 1)
    for i in xrange(samples):
        ax.scatter(newdata[i, 0], newdata[i, 1], newdata[i, 2])
#         ax.scatter(newdata[i, 0], newdata[i, 1])
    for i in xrange(samples):
        ax.text(newdata[i, 0], newdata[i, 1], newdata[i, 2], labels[i])
#         ax.annotate(labels[i], (newdata[i, 0], newdata[i, 1]))
    plt.xlabel('SVD1')
    plt.ylabel('SVD2')
    plt.show()
    
svd(data, 3)
