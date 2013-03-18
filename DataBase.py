#!/usr/bin/python
#-*- coding: utf-8 -*-

import wikiDataGatherer

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
  return data
