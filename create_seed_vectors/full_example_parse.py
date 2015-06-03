#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import re


def process_document(document):
    d = document.replace(u'…', '.').replace(' \' ', '\'')
    d = re.sub( '\s+', ' ', d ).strip()
    d = re.sub(r'[^\x00-\x7F]+',' ', d)
    return d