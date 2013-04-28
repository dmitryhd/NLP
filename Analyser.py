#!/usr/bin/python3
#-*- coding: utf-8 -*-

import glob
import os
import re
import sys
import operator
from subprocess import Popen, PIPE
from DataBase import *


min_cnt = 1 # minimum number of word in document for word to be considered
max_words = 100 # maximum number of words in frequency dictionary

def classify_articles (articles_file_names,
             db_name_a='data_bases/sciAm2008-2011.db',
             db_name_b='data_bases/fiction.db'):
    """ bayesian classify given articles to class A, or B"""
    total_word_prob_a = GetTotalWordProb(db_name_a)
    articles_a = GetAllArticlesNormalized (db_name_a)
    total_word_prob_b = GetTotalWordProb(db_name_b)
    articles_b = GetAllArticlesNormalized (db_name_b)
    for fname in articles_file_names:
        print("classify article: {}".format(fname))
        with open('data/' + fname, 'r') as fd:
            text = fd.read()
        norm_fd = NormalizeDict(GetFrequencyDict(NormalizeText(text)))
        prob_text_belong_to_a = BayesProb(norm_fd, total_word_prob_a)
        prob_text_belong_to_b = BayesProb(norm_fd, total_word_prob_b)
        value = 0
        if prob_text_belong_to_a > prob_text_belong_to_b:
            value = prob_text_belong_to_a/prob_text_belong_to_b
            print ('article %30s belongs to class A, p_a/p_b = %e' % (fname, value))
        else:
            value = prob_text_belong_to_b/prob_text_belong_to_a
            print ('article %30s belongs to class B, p_b/p_a = %e' % (fname, value))


# -------------- bayes
def GetTotalWordProb (dbname):
    """ for every word in cluster: get prob. that word is in document) """
    sqlOpRead = SQLOperator(dbname)
    articles = sqlOpRead.ReadAllArticles()
    total_dict = GetTotalFreqDict ([article.freqDict for article in articles])
    total_word_prob = {}
    for article in articles:
        for word in article.freqDict.keys():
            if (word not in total_word_prob.keys()):
                total_word_prob[word] = 1
            else:
                total_word_prob[word] += 1
                total_word_prob[word] = int(total_word_prob[word])
    for word in total_word_prob.keys():
        if total_word_prob[word] == 0:
            continue
        total_word_prob[word] = float (total_word_prob[word])/len(articles)
        assert total_word_prob[word] # not equals 0
    PrintFancyDict(total_word_prob, 10000)
    return total_word_prob


def BayesProb (art_norm_fd, total_word_prob):
    min_prob = min(total_word_prob.values())
    p = 1
    if not min_prob:
        min_prob = 0.1
    for word in art_norm_fd:
        if word not in total_word_prob:
            p *= min_prob
        else:
            p *= total_word_prob[word]
    return p


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


def PrintFancyDict (freq_dict, max_cnt = 100):
    x = sorted(freq_dict.items(), key=operator.itemgetter(1), reverse=True)
    cnt = 0
    for i in x:
        print ("%50s %.5f" % (i[0], i[1]))
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

def NormalizeDict (freq_dict):
    """ get only most valuable words, if wc = 1 - ignore """
    total_cnt = 0
    for key in freq_dict.keys():
        total_cnt += freq_dict[key]
    normalized_dict = {}
    for key in freq_dict.keys():
        if freq_dict[key] < min_cnt:
            continue
        normalized_dict[key] = float(freq_dict[key])/total_cnt
    # normalized_dict
    res = {}
    cnt = 0
    for w in sorted(normalized_dict, key=normalized_dict.get, reverse=True):
        if cnt == max_words:
            break
        res[w] = normalized_dict[w]
        cnt += 1
    return res

def GetAllArticlesNormalized(dbname):
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


def GetSeparateTextsFromTXT (fiction_dir='data/fiction/',
                             db_path='data_bases/fiction.db'):
    """ Get name of directory full of text files, create articles for them
        and store to given db file"""
    articles = []
    article_id = 0
    current_dir = os.getcwd()
    os.chdir(fiction_dir)
    for file_name in glob.glob('*.txt'):
        with open(file_name, 'r') as fd:
            text = fd.read()
        norm_text = NormalizeText(text)
        print("******* preparing article from {}".format(file_name))
        article = Article(article_id, "fic", file_name, text,
                          norm_text, GetFrequencyDict(norm_text))
        article_id += 1
        articles.append(article)
    os.chdir(current_dir)
    SaveArticlesToDB(articles, db_path)
    return articles


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
#    norm_articles = GetAllArticlesNormalized(sys.argv[1])
#    for a in norm_articles.keys():
#        print ("{} ->".format(a))
#        PrintFancyDict (norm_articles[a],15)
#        print ("==================")
    #main(sys.argv[1])
    to_compare = [
                    'A_Christmas_Carol-Charles_Dickens.txt',
                    'A_Descent_Into_the_Maelstrom-Edgar_Allan_Poe.txt'
            ]
    classify_articles(to_compare)
    #main('data_bases/sciAm2008-2011.db')
    #GetSeparateTextsFromTXT('data/fiction','data_bases/fiction.db')
