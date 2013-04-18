#!/usr/bin/python2
#-*- coding: utf-8 -*-
import nltk

st = nltk.stem.lancaster.LancasterStemmer()
goodPOS = ('FW', 'JJ', 'JJR', 'JJS', 'NN', 'NNP', 'NNPS', 'NNS', 'RB', 'VB', "VBD", "VBG", "VBN", "VBP", "VBZ")
with open ("exchange_inp.txt", 'r') as rfd:
    text = rfd.read()
print "Start normalization process ... "
print "tokenizing ... "
toc = nltk.word_tokenize(text)
print "pos tagging ... "
pos = nltk.pos_tag(toc)

print "remove pos tags ... "
normtext = [st.stem(p[0]) for p in pos if len(p[0]) > 3 and p[1] in goodPOS]
with open ("exchange_out.txt", 'w') as wfd:
    for w in normtext:
        wfd.write(w + ' ')
