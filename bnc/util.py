#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''
Created on May 25, 2015

@author: Tuan Do
'''
import re


def process_document(document):
    d = document.replace(',', ' , ').replace(u'‘', '\'').replace(u'’', '\'')\
                        .replace(u'`', '\'').replace(u'–', '-').replace(u'—', '-')\
                        .replace('.', ' . ')\
                        .replace(' \'', '\'')\
                        .replace(':', ' : ').replace(';', ' ; ')\
                        .replace('\'', ' \' ')
    d = re.sub( '\s+', ' ', d ).strip()
    return d

def process_sentence(sentence):
    d = sentence.replace('<p>', ' ').replace('<\/p>',' ').replace(u'‘', '\'').replace(u'’', '\'')\
                        .replace(u'`', '\'').replace(u'–', '-').replace(u'—', '-')\
                        .replace(',', ' , ')\
                        .replace('.', ' . ')\
                        .replace(')', ' )').replace('(', '( ')\
                        .replace(']', ' ]').replace('[', '[ ')\
                        .replace('&quot;', ' " ')\
                        .replace(':', ' : ').replace(';', ' ; ')\
                        .replace('\'', ' \' ').replace('--', '-')
    d = re.sub( '\s+', ' ', d ).strip()
    return d