#!/usr/bin/python2
#-*- coding: utf-8 -*-

# Author: Dmitryh Khodakov <dmitryhd@gmail.com>

""" Module for normalize text: stemming and removing some parts of speech from it """

import nltk

# use stemmer 
st = nltk.stem.lancaster.LancasterStemmer()

goodPOS = ('FW', 'JJ', 'JJR', 'JJS', 'NN', 'NNP', 'NNPS', 'NNS', 'RB', 'VB', "VBD", "VBG", "VBN", "VBP", "VBZ")

# read text:
with open ("exchange_inp.txt", 'r') as rfd:
    text = rfd.read()

toc = nltk.word_tokenize(text)
pos = nltk.pos_tag(toc)

# forbrid some parts of speech
normtext = [st.stem(p[0]) for p in pos if len(p[0]) > 3 and p[1] in goodPOS]
# write result to file
with open ("exchange_out.txt", 'w') as wfd:
    for w in normtext:
        wfd.write(w + ' ')
