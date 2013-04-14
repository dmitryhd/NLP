#!/usr/bin/python
#-*- coding: utf-8 -*-
import Analyser
import DataBase
def main ():
  rawData = DataBase.GetDataFromSavedWikiPages("wikipedia")
  freqDict = Analyser.GetFrequencyDict (rawData)
  Analyser.PrintFreqDict (freqDict, "fd.txt")
  #GetWikipediaPages (numberOfPagesToDownload = 10000, folderName = "wikipedia")


if __name__ == '__main__':
  main()
