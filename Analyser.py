#!/usr/bin/python
#-*- coding: utf-8 -*-


# @arg rawtext (utf string) text from which frequncy dict is formed
def GetFrequencyDict (rawtext, lang = "ru"):
  """ generate dictionary {word: wordcount} from normal forms of word """
  # morphology analizer
#  if lang == "ru":
#    morph = get_morph ("dict/ru")
#  elif (lang == "en"):
#    morph = get_morph ("dict/en")
#  else:
#    raise ValueError ("Wrong language argument!")
  #TODO Generate list of acceptable words.
  acceptableWords = rawtext.split()

  # Frequency dict creation.
  totalWordCnt = 0
  uniqueWordCnt = 0
  frequencyDict = {}
  for word in acceptableWords:
    totalWordCnt += 1
    if word in frequencyDict:
      frequencyDict [word] += 1
    else:
      frequencyDict [word] = 1
      uniqueWordCnt += 1
  return frequencyDict

# TODO: @arg
def PrintFreqDict (wdict, fileName, maxWordsPrint = 10):
  # write result to file
  fend = open (fileName, 'w', encoding='utf-8')
  wordCnt = 0
  for w in sorted (wdict, key=wdict.get, reverse=True):
    string = w + " " + str (wdict[w]) 
    if wordCnt < maxWordsPrint:
      print (string)
    wordCnt += 1
    fend.write (string + "\n") 
  fend.close ()
