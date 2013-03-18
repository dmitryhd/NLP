#!/usr/bin/python
#-*- coding: utf-8 -*-

# @arg rawtext (utf string) text from which frequncy dict is formed
def GetFrequencyDict (rawtext):
  """ generate dictionary {word: wordcount} from normal forms of word """
  #TODO
  blacklist = [
  "без", "близ",
  "в", "вместо", "вне", "для", "до", "за", "из", "из-за", "из-под", "к", "кроме", "между", "меж",
  "ко", "на", "над", "надо", "о", "об", "обо", "от", "ото", "перед", "передо", "пред", "предо",
  "пo", "под", "подо", "при", "про", "ради", "с", "со", "сквозь", "среди", "у", "через", "чрез",
  "а", "вдобавок", "именно", "также", "то", "благодаря", "будто", "вдобавок",
  "вопреки", "ввиду", "да", "нет", "и", "не", "ни", "же", "едва", "если", "бы", "затем", "зато", "зачем",
  "именно", "поэтому", "кабы", "как", "когда", "либо", "чтобы", "что",
  "он", "oно", "она", "они", "я", "мы", "ты", "по", "так", "или", "этот", "но", "наш", "ну"
  ]
  outputFile = 'outputfile.txt'
  inputFile = 'inputfile.txt'
  fdin = open (inputFile, 'w', encoding='utf-8')
  fdin.write (rawtext)
  fdin.close ()
  #TODO
  os.system ('mystem.exe  -e utf-8 {} {}'.format(inputFile, outputFile))
  fdout = open (outputFile, 'r', encoding='utf-8')
  parsedtext = fdout.read ()
  fdout.close ()
  # find one word in parentesis
  matches = re.findall ( r"\{(\w+)\}", parsedtext, re.M|re.I|re.U)
  totalWordCnt = 0
  uniqueWordCnt = 0
  wdict = {}
  for word in matches:
    if (len(word) <= 2):
      continue
    if word in blacklist:
      continue
    totalWordCnt += 1
    if word in wdict:
      wdict [word] += 1
    else:
      wdict [word] = 1
      uniqueWordCnt += 1
  return wdict


def PrintFreqDict (wdict, fileName):
  maxWordsPrint = 10
  #print ("Total words: {}, unique {}.".format (totalWordCnt, uniqueWordCnt))
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
