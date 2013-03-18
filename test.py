#!/usr/bin/python
#-*- coding: utf-8 -*-

import unittest
import logging
from wikiDataGatherer import *

# ----------- Unit tests -------------
class TestFrequencyDict (unittest.TestCase):

  def testParser (self):
    htmlDoc = "<!DOCTYPE html><html><body><h1>AAA</h1><h3 class=\"offer\">OFFER</h3>\
    <p>w1</p>\
    <l>w2</l>\
    <p>w3</p>\
    <p>w4</p>\
    </body></html>"
    parser = GetInfoInTagParser (["p"])
    parser.feed (htmlDoc)
    expected = "w1 w3 w4"
    print (parser.m_currentData)
    self.assertEqual (parser.m_currentData.strip(), expected)

  def testFreqDict (self):
    rawtext = "Привет, простой текст, давай посмотрим на что способен простой 1212 ! , ыыыва простой давай ПАрсСер!121"
    freqDict = GetFrequencyDict (rawtext)
    #PrintFreqDict (freqDict, "fd_test.txt")
    expected = {
      "давать": 2,
      "текст": 1,
      "способный": 1,
      "посмотреть": 1,
      "привет": 1}
    self.assertEqual (freqDict, expected)

if __name__ == '__main__':
  unittest.main()
