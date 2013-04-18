#!/usr/bin/python
#-*- coding: utf-8 -*-

import wikiDataGatherer
import sqlite3
import pickle


class Article (object):
    def __init__(self, index=-1, atype="sci", name=None, text=None, normtext=None, freqDict=None):
        self.index = index
        self.atype = atype
        self.name = name
        self.text = text
        self.normtext = normtext
        self.freqDict = freqDict

    def __repr__(self):
        subdict = {}
        cnt = 0
        for i,j in self.freqDict.items():
            if cnt < 10:
                subdict[i] = j
            cnt += 1
        return "article: {} {} {}, symb: {} dict: {}".format(self.index, self.atype, self.name, len(self.normtext), subdict)

    def __eq__(self, other):
        # print (self, other)
        # return self.__dict__ == other.__dict__
        if self.text == other.text and self.atype == other.atype and self.text == other.text and self.name == other.name:
            return True
        return False


class SQLOperator ():
    def __init__(self, dbName):
        self.dbName = dbName
        self.conn = sqlite3.connect(dbName)

    def SaveArticle(self, article):
        res = False
        try:
            res = self.conn.cursor().execute('SELECT * FROM articles ORDER BY id')
        except:
            print ("creating new table I")
            self.conn.cursor().execute(
                'CREATE TABLE articles (id text, atype text, name text, txt text, normtxt text, freqdict text)')
        if not res:
            try:
                print ("creating new table II")
                self.conn.cursor().execute(
                    'CREATE TABLE articles (id text, atype text, name text, txt text, normtxt text, freqdict text)')
            except:
                print ("creating new table - fail!!!")
                pass
        print ("Saving...")
        self.conn.cursor().execute("INSERT INTO articles VALUES (?,?,?,?,?,?)", (str(
            article.index), article.atype, article.name, article.text, article.normtext, pickle.dumps(article.freqDict)))

    def ReadAllArticles(self):
        dbContent = []
        for row in self.conn.cursor().execute('SELECT * FROM articles ORDER BY atype'):
            article = Article(row[0], row[1], row[
                              2], row[3], row[4], pickle.loads(row[5]))
            #print("get art! {}".format(article))
            dbContent.append(article)
            #print ("-- read article {}".format(article))
        return dbContent

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()


# @arg filename - unicode string - Name of file to save (will be rewrited)
# @return unicode string - Html page content
def GetPageFromFile(filename):
    fd = open(filename, 'r', encoding='utf-8')
    page = fd.read()
    fd.close()
    return page


# @arg page - unicode string - Html page content
# @arg filename - unicode string - Name of file to save (will be rewrited)
def SavePageToFile(page, filename):
    fd = open(filename, 'w', encoding='utf-8')
    print("saving page: to {}".format(filename))
    fd.write(page)
    fd.close()


# @arg nameOfFolder (utf string) name of folder to seek for ht
# TODO: @return
def GetDataFromSavedWikiPages(folderName="wikipedia"):
    """ generate dictionary {word: wordcount} from normal forms of word """
    data = ""
    for i in range(1, 2500):
        filename = folderName + "/ruwiki_page_" + str(i) + ".html"
        print(filename)
        page = GetPageFromFile(filename)
        currentPageData = wikiDataGatherer.GetRawTextFromWikiPage(page)
        data += currentPageData
    retur
