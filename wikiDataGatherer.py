#!/usr/bin/python
#-*- coding: utf-8 -*-

import os
import re
import time
import random
from urllib.request import *

from html.parser import HTMLParser

class GetInfoInTagParser (HTMLParser):
  """ used to get data in specified tag (in this case - in <p> tag, where all plain text from ru.wikipedia.org article stored) """
  def __init__ (self, tags):
    HTMLParser.__init__ (self)
    self.m_currentData = ""
    self.m_tags = tags
    self.m_isTagEncountered = [False]*len (tags);

  # Activate when sees opening tag. Seeks tag matches in defined list. Changes inner state
  def handle_starttag (self, tag, attrs):
    if (tag in self.m_tags):
      tagIndex = self.m_tags.index(tag)
      # check attr if set any:
      self.m_isTagEncountered [tagIndex] = True
      if (len(self.m_isTagEncountered) > 1):
        self.m_isTagEncountered [tagIndex - 1] = False

  # Activate when sees endings tag. Seeks tag matches in defined list. Changes inner state
  def handle_endtag (self, tag):
    if (tag in self.m_tags):
      tagIndex = self.m_tags.index(tag)
      self.m_isTagEncountered[tagIndex] = False

  # Activate when sees data between opening and ending tags, that are seeked.
  def handle_data (self, data):
    if (True in self.m_isTagEncountered):
      self.m_currentData += " " + data


# @arg url - unicode string - Html page url
# @return unicode string - Html page content
def GetURL (url):
  """ Get HTML page by its URL """
  headers = { 'User-Agent' : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.56 Safari/537.17" }
  req = Request (url, None, headers)
  response = urlopen (req)
  return response.read ().decode('utf-8')


# @arg numberOfPagesToDownload (int) - total number of random articles requests
# @return none
def GetWikipediaPages (numberOfPagesToDownload = 10000, folderName = "wikipedia"):
  """Get number of ru.wiki random articles and save them in given folder"""
  filePrefix = folderName + "/ruwiki_page_"
  iteration = 0
  # ru.wikipedia - random page
  url = "http://ru.wikipedia.org/wiki/%D0%A1%D0%BB%D1%83%D0%B6%D0%B5%D0%B1%D0%BD%D0%B0%D1%8F:%D0%A1%D0%BB%D1%83%D1%87%D0%B0%D0%B9%D0%BD%D0%B0%D1%8F_%D1%81%D1%82%D1%80%D0%B0%D0%BD%D0%B8%D1%86%D0%B0"
  while iteration < numberOfPagesToDownload:
    page = GetURL (url)
    savedPageFileName = filePrefix + str(iteration) + ".html"
    SavePageToFile (page, savedPageFileName)
    print ("get page: size = {}, totalpageNumber = {}".format(len(page),iteration))
    time.sleep (1 + 0.05 * random.randrange (1, 20)) # wait 1-2 seconds for not being suspected ;-)
    iteration += 1


def GetRawTextFromWikiPage (page):
  parser = GetInfoInTagParser (["p"])
  parser.feed (page)
  return parser.m_currentData

def main ():
  freqDict = GetFreqDictFromSavedWikiPages("wikipedia")
  PrintFreqDict (freqDict, "fd.txt")
  #GetWikipediaPages (numberOfPagesToDownload = 10000, folderName = "wikipedia")


if __name__ == '__main__':
  main()
