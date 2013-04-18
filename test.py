#!/usr/bin/python
#-*- coding: utf-8 -*-

import os
import unittest
import wikiDataGatherer
import DataBase
import Analyser
from Analyser import *
from DataBase import *

# ----------- Unit tests -------------


class TestWikiDataGatherer (unittest.TestCase):
    def testGetRawTextFromValidPage(self):
        htmlDoc = "<!DOCTYPE html><html><body><h1>AAA</h1><h3 class=\"offer\">OFFER</h3>\
    <p>w1</p>\
    <l>w2</l>\
    <p>w3</p>\
    <p>w4</p>\
    </body></html>"
        result = wikiDataGatherer.GetRawTextFromWikiPage(htmlDoc)
        expected = "w1 w3 w4"
        self.assertEqual(result, expected)

    def testGetRawTextFromEmptyPage(self):
        htmlDoc = ""
        result = wikiDataGatherer.GetRawTextFromWikiPage(htmlDoc)
        expected = ""
        self.assertEqual(result, expected)

    def testGetRawTextFromPageWithoutP(self):
        htmlDoc = "<h3 class=\"offer\">OFFER</h3>"
        result = wikiDataGatherer.GetRawTextFromWikiPage(htmlDoc)
        expected = ""
        self.assertEqual(result, expected)

    def testGetRawTextFromInvalidPage(self):
        htmlDoc = "<h3 class=\"offer\">OFFER <p>w1"
        result = wikiDataGatherer.GetRawTextFromWikiPage(htmlDoc)
        expected = "w1"
        self.assertEqual(result, expected)

    # TODO other parser tests
    # def testGetUrl (self):
        # page = wikiDataGatherer.GetURL ("http://google.com")
        # self.assertNotEqual (page, "")
    # TODO other page tests, mb custom server

    # WikipediaGetter test.


class TestGetText (unittest.TestCase):
    def testSimpleGetText(self):
        text = Analyser.GetTexts('testpdf01')
        self.assertEqual (text[:27], 'Proceedings of the IEEE Wor')

    def testRecursive(self):
        text = Analyser.GetTexts('testpdf02')
        self.assertEqual (text[:27], 'Proceedings of the IEEE Wor')


class TestDataBase (unittest.TestCase):
    def testSavePage(self):
        testFilename = "testfile.html"
        originalPage = "smth in unicode and русский"
        DataBase.SavePageToFile(originalPage, testFilename)
        newPage = DataBase.GetPageFromFile(testFilename)
        self.assertEqual(originalPage, newPage)
        os.remove(testFilename)

    def testGetDataFromSavedWikiPages(self):
        folderName = "wikipedia"
        # TODO

    def testSqlOneArticle(self):
        """ sql save of one page """
        text = "aaa bbbb cccc dddd dfvsdf aaa"
        fd = GetFrequencyDict (text)
        article = DataBase.Article(1, "sci", "name1", text, text, fd)
        try:
            os.remove("test.db")
        except:
            print ("no such file")
        sqlOpWrite = DataBase.SQLOperator("test.db")
        sqlOpWrite.SaveArticle(article)
        sqlOpWrite.commit()
        articles = sqlOpWrite.ReadAllArticles()
        expectedArticles = [article]
        self.assertEqual(articles, expectedArticles)
        print("---- get article {}, expected {}".format(articles, expectedArticles))
        sqlOpWrite.close()


class TestMorphologicalAnalyser(unittest.TestCase):
    def testSimpleLemmatizer(self):
        """ just simple test case"""
        text = "cats"
        expected = "cat"
        normalized = Analyser.NormalizeText(text)
        self.assertEqual(normalized, expected)

    def testComplexLemmatizer(self):
        """ Lancaster stemmer test """
        checklist = {'text': 'text',
                     'texts': 'text',
                     'give': 'giv',
                     'giving': 'giv',
                     'provided': 'provid',
                     'texts give': 'text giv',
                     'using': 'us'}
                     #'is': 'be',
                     #'gave': 'giv',
#                     'texts, gave': 'text give'}
        for text, expected in checklist.items():
            print (text, expected)
            self.assertEqual(Analyser.NormalizeText(text), expected)


class TestFrequencyDict (unittest.TestCase):
    def testLemmatizatorEnglishSimple(self):
        rawtext = "hello bob lets see articles given hellos"
        normtext = Analyser.NormalizeText (rawtext)
        freqDict = Analyser.GetFrequencyDict(normtext)
        # PrintFreqDict (freqDict, "fd_test.txt")
        expected = {
            "hello": 2,
            "let": 1,
            "artic": 1,
            "giv": 1}
        self.assertEqual(freqDict, expected)

    def testHardText(self):
        rawtext = "Привет, простой текст, давай посмотрим на что способен простой 1212 ! , ыыыва простой давай ПАрсСер!121"
        freqDict = Analyser.GetFrequencyDict(rawtext)
        # PrintFreqDict (freqDict, "fd_test.txt")
        expected = {
            "давать": 2,
            "текст": 1,
            "способный": 1,
            "посмотреть": 1,
            "привет": 1}
    #  self.assertEqual (freqDict, expected)

    def testEmptyText(self):
        rawtext = ""
        freqDict = Analyser.GetFrequencyDict(rawtext)
        expected = {}
        self.assertEqual(freqDict, expected)

    def testSimpleTextEng(self):
        rawtext = "omg hello hello python"
        freqDict = Analyser.GetFrequencyDict(rawtext)
        expected = {"omg": 1, "hello": 2, "python": 1}
        self.assertEqual(freqDict, expected)

    def testSimpleTextRus(self):
        rawtext = "что привет привет питон"
        freqDict = Analyser.GetFrequencyDict(rawtext)
        expected = {"что": 1, "привет": 2, "питон": 1}
        self.assertEqual(freqDict, expected)

if __name__ == '__main__':
    unittest.main()
