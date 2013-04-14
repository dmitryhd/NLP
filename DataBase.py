#!/usr/bin/python
#-*- coding: utf-8 -*-

import wikiDataGatherer
import sqlite3


class Article (object):
  def __init__ (self, index = -1, atype = "sci", text="none"):
    self.text = text
    self.atype = atype
    self.index = index

  def __str__(self):
    return "article: {} {} {}".format (self.index, self.atype, self.text)

  def __repr__  (self):
    return "article: {} {} {}".format (self.index, self.atype, self.text)

  def __eq__ (self, other):
    #print (self, other)
    #return self.__dict__ == other.__dict__
    if self.text == other.text and self.atype == other.atype and self.text == other.text:
      return True
    return False


# @arg filename - unicode string - Name of file to save (will be rewrited)
# @return unicode string - Html page content
def GetPageFromFile (filename):
  fd = open (filename, 'r', encoding='utf-8')
  page = fd.read ()
  fd.close ()
  return page


# @arg page - unicode string - Html page content
# @arg filename - unicode string - Name of file to save (will be rewrited)
def SavePageToFile (page, filename):
  fd = open (filename, 'w', encoding='utf-8')
  print ("saving page: to {}".format (filename))
  fd.write (page)
  fd.close ()


# @arg nameOfFolder (utf string) name of folder to seek for ht
# TODO: @return
def GetDataFromSavedWikiPages (folderName = "wikipedia"):
  """ generate dictionary {word: wordcount} from normal forms of word """
  data = ""
  for i in range(1,2500):
    filename = folderName + "/ruwiki_page_" + str(i) + ".html"
    print(filename)
    page = GetPageFromFile (filename)
    currentPageData = wikiDataGatherer.GetRawTextFromWikiPage (page)
    data += currentPageData
  retur


class SQLOperator ():
  def __init__ (self, dbName):
    self.dbName = dbName
    self.conn = sqlite3.connect (dbName)
    self.cursor = self.conn.cursor ()

  def SaveArticle (self, article):
    res = False
    try:
      res = self.cursor.execute('SELECT * FROM articles ORDER BY id')
    except:
      self.cursor.execute ('CREATE TABLE articles (id text, atype text, page text)')
    if not res:
      try:
        self.cursor.execute ('CREATE TABLE articles (id text, atype text, page text)')
      except:
        pass
    self.cursor.execute ("INSERT INTO articles VALUES (?,?,?)", (str(article.index), article.atype, article.text))

  def ReadAllArticles (self):
    dbContent = []
    for row in self.cursor.execute('SELECT * FROM articles ORDER BY atype'):
      article = Article (row[0], row[1], row[2])
      print ("get art! {}".format(article))
      dbContent.append(article)
    return dbContent
# TODO: 
#  def ReadArticles (atype):

  def commit (self):
    self.conn.commit ()

  def close (self):
    self.conn.close ()
