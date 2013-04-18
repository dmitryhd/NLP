#!/usr/bin/python
#-*- coding: utf-8 -*-

import glob
import os
import re
import sys
import operator
from subprocess import Popen, PIPE
from DataBase import *

# ------------- functions to prepare parsed articles for analysis
def IntercectDicts (listOfDicts):
    base = listOfDicts[0]
    basek = base.keys()
    for d in listOfDicts:
        basek = [val for val in basek if val in d.keys()]
    res = {}
    for key in basek:
        res [key] = base[key]
    return res


def PrintFancyDict (freq_dict, max_cnt = 20):
    x = sorted(freq_dict.items(), key=operator.itemgetter(1), reverse=True)
    cnt = 0
    for i in x:
        print ("%11s %.5f" % (i[0], i[1]))
        if cnt > max_cnt:
            return
        cnt += 1


def GetTotalFreqDict (list_of_norm_dicts):
    def UnionDicts (listOfDicts):
        baseset = set(listOfDicts[0].keys())
        for d in listOfDicts:
            s = set(d.keys())
            baseset = baseset|s
        return baseset
    # get union of keys
    keys = UnionDicts(list_of_norm_dicts)
    cnts = [0]*len(keys)
    i = 0
    for k in keys:
        for d in list_of_norm_dicts:
            if k in d:
                cnts[i] += d[k]
        i += 1
    res = {}
    i = 0
    for k in keys:
        res[k] = cnts[i]
        i += 1
    return res


def GetAllArticlesNormalized(dbname):
    def NormalizeDict (freq_dict):
        total_cnt = 0
        for key in freq_dict.keys():
            total_cnt += freq_dict[key]
        normalized_dict = {}
        for key in freq_dict.keys():
            normalized_dict[key] = float(freq_dict[key])/total_cnt
        return normalized_dict
    sqlOpRead = SQLOperator(dbname)
    articles = sqlOpRead.ReadAllArticles()
    normalized_articles = {article.name:NormalizeDict(article.freqDict) for article in articles}
    return normalized_articles

# ----------------- functions to parse articles

def AnalyzeTexts(directory):
    """ get freq dict """
    text = GetTexts(directory)
    normtext = NormalizeText(text)
    fd = GetFrequencyDict(text)
    PrintFreqDict(fd, '/tmp/fd.dat')

def SaveArticlesToDB (articles, dbfile='xx.db'):
    sqlOpWrite = SQLOperator(dbfile)
    for a in articles:
        sqlOpWrite.SaveArticle(a)
    sqlOpWrite.commit()
    sqlOpWrite.close()
    sqlOpRead = SQLOperator(dbfile)
    rarticles = sqlOpRead.ReadAllArticles()
    print("------------ saved {} articles, total {}".format(len(articles),len(rarticles)))


def AnalyzeTextsSeparately(directory, dbfile="sci_articles.db"):
    articles = GetSeparateTextsFromPDF(directory)
    try:
        sqlOpWrite = SQLOperator(dbfile)
        for a in articles:
            sqlOpWrite.SaveArticle(a)
        sqlOpWrite.commit()
        sqlOpWrite.close()

        sqlOpRead = SQLOperator(dbfile)
        rarticles = sqlOpRead.ReadAllArticles()
        for a in rarticles:
            print(a)
    except:
        pass
    return articles


def StripString(string):
    return (''.join(c if c.isupper() or c.islower() else ' ' for c in string)).lower()


def NormalizeText(text):
    main_wd = '/home/dimert/repos/NLP'
    cwd = os.getcwd()
    os.chdir(main_wd)
    # tokenizing
    text = StripString(text)
    with open("exchange_inp.txt", 'w') as wfd:
        wfd.write(text)
    os.system('python2 normalize.py')
    with open("exchange_out.txt", 'r') as rfd:
        text = rfd.read()
    os.chdir(cwd)
    return text.strip()


def GetSeparateTextsFromPDF(directory):
    """ recusively get all text from given directory """
    def CreateArticlesFromThisDirectory(begin_id=0):
        """ get all texts from current directory, return list of articles"""
        pdftotextcommand = ['pdftotext', '-enc', 'UTF-8']
        articles = []
        articleid = begin_id
        for filename in glob.glob('*.pdf'):
            print("handle file: {}".format(filename))
            command = pdftotextcommand + [filename, 'tmp']
            process = Popen(command, stdout=PIPE)
            exit_code = os.waitpid(process.pid, 0)
            output = process.communicate()[0]
            with open('tmp', 'r') as fd:
                text = fd.read()
                norm_text = NormalizeText(text)
                print("******* preparing article from {}".format(filename))
                article = Article(
                    articleid, "sci", filename, text, norm_text, GetFrequencyDict(norm_text))
                print("******* created {}".format(article))
                articles.append(article)
            os.remove('tmp')
            articleid += 1
        return articles

    os.chdir(directory)
    currentwd = os.getcwd()
    result = CreateArticlesFromThisDirectory()
    article_id = len(result)
    for innerdirectory in [directory[1] for directory in os.walk('.')]:
        if not innerdirectory:
            continue
        innerdirectory = innerdirectory[0]
        try:
            os.chdir(innerdirectory)
        except:
            print("can't cd dir to {}".format(innerdirectory))
            continue
        result.append(CreateArticlesFromThisDirectory(article_id))
        article_id = len(result)
        os.chdir(currentwd)
    os.chdir("..")
    print("End of getting data")
    return result


# TODO: rewrite!
def GetTexts(directory):
    """ recusively get all text from given directory """
    def _getpdf():
        """ get all texts from current directory """
        pdftotextcommand = ['pdftotext', '-enc', 'UTF-8']
        result = ''
        for f in glob.glob('*.pdf'):
            print("handle file: {}".format(f))
            command = pdftotextcommand + [f, 'tmp']
            process = Popen(command, stdout=PIPE)
            exit_code = os.waitpid(process.pid, 0)
            output = process.communicate()[0]
            with open('tmp', 'r') as fd:
                text = fd.read()
                result += text + ' '
            os.remove('tmp')
        return result

    os.chdir(directory)
    currentwd = os.getcwd()
    result = _getpdf()
    for innerdirectory in [x[1] for x in os.walk('.')]:
        if not innerdirectory:
            continue
        innerdirectory = innerdirectory[0]
        try:
            os.chdir(innerdirectory)
        except:
            print("can't cd dir to {}".format(innerdirectory))
            continue
        result += _getpdf()
        os.chdir(currentwd)
    os.chdir("..")
    print("End of getting data")
    return result


# @arg rawtext (utf string) text from which frequncy dict is formed
def GetFrequencyDict(rawtext, lang="ru"):
    """ generate dictionary {word: wordcount} from normal forms of word """
    print("Get freq dict ...")
    acceptableWords = rawtext.split()

    # Frequency dict creation.
    totalWordCnt = 0
    uniqueWordCnt = 0
    frequencyDict = {}
    for word in acceptableWords:
        totalWordCnt += 1
        if word in frequencyDict:
            frequencyDict[word] += 1
        else:
            frequencyDict[word] = 1
            uniqueWordCnt += 1
    print("done ... ")
    return frequencyDict


def PrintFreqDict(wdict, fileName, maxWordsPrint=10):
    # write result to file
    fend = open(fileName, 'w', encoding='utf-8')
    wordCnt = 0
    for w in sorted(wdict, key=wdict.get, reverse=True):
        string = w + " " + str(wdict[w])
        if wordCnt < maxWordsPrint:
            print(string)
        wordCnt += 1
        fend.write(string + "\n")
    fend.close()


if __name__ == '__main__':
    # AnalyzeTexts('data_sci')
    # print("total: {} keywords".format(len(total_dict)))
    # PrintFancyDict(total_dict, 100)
    norm_articles = GetAllArticlesNormalized(sys.argv[1])
    for a in norm_articles.keys():
        print ("{} ->".format(a))
        PrintFancyDict (norm_articles[a],15)
        print ("==================")
