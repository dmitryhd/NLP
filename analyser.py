#!/usr/bin/python3
#-*- coding: utf-8 -*-

# Author: Dmitryh Khodakov <dmitryhd@gmail.com>

""" Main text analysing module """

import glob
import os
import operator
from subprocess import Popen, PIPE
import sqlite3
import pickle


MinCnt = 1  # minimum number of word in document for word to be considered
MaxWords = 50  # maximum number of words in frequency dictionary


class Article (object):
    """ any text representation """
    def __init__(self, index=-1, atype="sci", name=None, text=None, normtext=None, freq_dict=None):
        self.index = index
        self.atype = atype
        self.name = name
        self.text = text
        self.normtext = normtext
        self.freq_dict = freq_dict

    def __repr__(self):
        subdict = {}
        cnt = 0
        for i, j in self.freq_dict.items():
            if cnt < 10:
                subdict[i] = j
            cnt += 1
        return "article: {} {} {}, symb: {} dict: {}".format(self.index,
                                                             self.atype, self.name, len(self.normtext), subdict)

    def __eq__(self, other):
        # print (self, other)
        # return self.__dict__ == other.__dict__
        if self.text == other.text and self.atype == other.atype and self.name == other.name:
            return True
        return False


def SaveArticles (db_name, articles):
    """ Data base saver """
    conn = sqlite3.connect(db_name)
    conn.cursor().execute(
            'CREATE TABLE IF NOT EXISTS articles (id text, atype text, name text, txt text, normtxt text, freqdict text)')
    for article in articles:
        conn.cursor().execute("INSERT INTO articles VALUES (?,?,?,?,?,?)", (str(
            article.index), article.atype, article.name, article.text, article.normtext, pickle.dumps(article.freq_dict)))
    conn.commit()
    conn.close()


def ReadAllArticles (db_name):
    """ Get all articles in this db """
    conn = sqlite3.connect(db_name)
    db_content = []
    try:
        query_result = conn.cursor().execute('SELECT * FROM articles ORDER BY atype')
    except:
        print 'cannot read from this database {}'.format(db_name)
        return []
    for row in query_result:
        article = Article(row[0], row[1], row[
                              2], row[3], row[4], pickle.loads(row[5]))
        # print("get art! {}".format(article))
        db_content.append(article)
        # print ("-- read article {}".format(article))
    return db_content


def CreateBdOfArticles(directory_name, db_name):
    cwd = os.getcwd()
    os.chdir(directory_name)
    article_id = 0
    articles = []
    for fname in glob.glob('*.pdf'):
        print "classify article: {}".format(fname)
        file_name, file_extension = os.path.splitext(fname)
        if file_extension == '.pdf':
            pdftotextcommand = ['pdftotext', '-enc', 'UTF-8']
            command = pdftotextcommand + [fname, 'tmp']
            process = Popen(command, stdout=PIPE)
            os.waitpid(process.pid, 0)
            with open('tmp', 'r') as fd:
                text = fd.read()
            os.remove('tmp')
        else:
            with open(fname, 'r') as fd:
                text = fd.read()
        norm_text = NormalizeText(text)
        article = Article(article_id, "fic", file_name, text,
                          norm_text, GetFrequencyDict(norm_text))
        articles.append(article)
        article_id += 1
    os.chdir(cwd)    # save to Data Base
    SaveArticles(db_name, articles)


def ClassifyArticles(articles_db_filename,
                     db_name_a='data_bases/sciAm2008-2011.db',
                     db_name_b='data_bases/fiction.db'):
    """ bayesian classify given articles to class A, or B"""
    total_word_prob_a = GetTotalWordProb(db_name_a)
    total_word_prob_b = GetTotalWordProb(db_name_b)

    for article in ReadAllArticles(articles_db_filename):
        prob_text_belong_to_a = BayesProb(GetFrequencyDict(article.normtext), total_word_prob_a)
        prob_text_belong_to_b = BayesProb(GetFrequencyDict(article.normtext), total_word_prob_b)
        calculated_class = ''
        if prob_text_belong_to_a > prob_text_belong_to_b:
            calculated_class = 'A'
        else:
            calculated_class = 'B'
        print 'article %30s belongs to class %s, p_a %e p_b %e' %
                 (article.name, calculated_class, prob_text_belong_to_a, prob_text_belong_to_b)


def GetTotalWordProb(dbname):
    """ for every word in cluster: get prob. that word is in document)
        return dictionary: word -> probability that word is in any doc in cluster
    """
    # count probability that word is in document
    total_word_prob = {}
    articles = ReadAllArticles (dbname)
    for article in articles:
        for word in article.freq_dict.keys():
            if (word not in total_word_prob.keys()):
                total_word_prob[word] = 1
            else:
                total_word_prob[word] += 1
            # multiple somtheing by zero wouldn't be a gread idea :-)
            assert not total_word_prob[word] == 0
    for word in total_word_prob.keys():
        total_word_prob[word] = float(total_word_prob[word])/len(articles)
    return total_word_prob


def BayesProb(art_norm_fd, total_word_prob):
    """ Function to calculate probability, that text belongs to group with given total_word_prob dictionary
        arguments: frequency dict of given text, and total dictionary of all words in cluster
    """
    min_prob = min(total_word_prob.values())/2
                   # calculate minimum probability, for missing word.
    prob = 1  # result
    if not min_prob:
        min_prob = 0.01
    #print("---------")
    for word in art_norm_fd:
        if word not in total_word_prob:
     #       print ("word: {} prob: {}".format(word, min_prob))
            prob *= min_prob  # sure, we didn't mutiply by zero!
        else:
     #       print ("word: {} prob: {}".format(word, total_word_prob[word]))
            prob *= total_word_prob[word]
        assert not prob == 0
    return prob


def PrintFancyDict(freq_dict, max_cnt=100):
    """ Debug function:
        Print dictionary by decreasing word count (most important words - first)
        maximum number of words printed - max_cnt
    """
    sorted_dict = sorted(
        freq_dict.items(), key=operator.itemgetter(1), reverse=True)
    cnt = 0
    for item in sorted_dict:
        print "%50s %.5f" % (item[0], item[1])
        if cnt > max_cnt:
            return
        cnt += 1


def NormalizeText(text):
    """ Get text to normal form. Using python2 and nltk. WARNING: uncompatible! """
    def GetTextFromSting(string):
        """ Get only plain english text with spaces """
        return (''.join(c if c.isupper() or c.islower() else ' ' for c in string)).lower()
    main_wd = '/home/dimert/repos/NLP'
    cwd = os.getcwd()
    os.chdir(main_wd)
    # tokenizing
    text = GetTextFromSting(text)
    with open("exchange_inp.txt", 'w') as wfd:
        wfd.write(text)
    os.system('python2 normalize.py')
    with open("exchange_out.txt", 'r') as rfd:
        text = rfd.read()
    os.remove("exchange_out.txt")
    os.remove("exchange_inp.txt")
    os.chdir(cwd)
    return text.strip()


def GetFrequencyDict(rawtext):
    """ generate dictionary {word: wordcount} from normal forms of word
        Get only most valuable words (max_words variable)
        And convert counter to probability of word in this particular text
    """
    acceptableWords = rawtext.split()

    # Frequency dict creation.
    frequencyDict = {}
    for word in acceptableWords:
        if word in frequencyDict:
            frequencyDict[word] += 1
        else:
            frequencyDict[word] = 1

    # count all words in dictionary
    total_cnt = 0
    for key in frequencyDict.keys():
        total_cnt += frequencyDict[key]
    # convert counter to probability of word in this particular text
    normalized_dict = {}
    for key in frequencyDict.keys():
        if frequencyDict[key] < MinCnt:
            continue
        normalized_dict[key] = float(frequencyDict[key])/total_cnt
    # Get only most valuable words (max_words variable)
    most_freq_dict = {}
    cnt = 0
    for word in sorted(normalized_dict, key=normalized_dict.get, reverse=True):
        if cnt == MaxWords:
            break
        most_freq_dict[word] = normalized_dict[word]
        cnt += 1
    return most_freq_dict


def GetSeparateTextsFromTXT(fiction_dir='data/fiction/',
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
        print "******* preparing article from {}".format(file_name)
        article = Article(article_id, "fic", file_name, text,
                          norm_text, GetFrequencyDict(norm_text))
        article_id += 1
        articles.append(article)
    os.chdir(current_dir)

    # save to Data Base
    SaveArticles(db_name, articles)


def GetSeparateTextsFromPDF(directory, db_path='data_bases/sciAm2008-2011.db'):
    """ recusively get all text from given directory """
    def CreateArticlesFromThisDirectory(begin_id=0):
        """ get all texts from current directory, return list of articles"""
        pdftotextcommand = ['pdftotext', '-enc', 'UTF-8']
        articles = []
        articleid = begin_id
        for filename in glob.glob('*.pdf'):
            command = pdftotextcommand + [filename, 'tmp']
            process = Popen(command, stdout=PIPE)
            os.waitpid(process.pid, 0)
            with open('tmp', 'r') as fd:
                text = fd.read()
                norm_text = NormalizeText(text)
                print "******* preparing article from {}".format(filename)
                article = Article(
                    articleid, "sci", filename, text, norm_text, GetFrequencyDict(norm_text))
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
            print "can't cd dir to {}".format(innerdirectory)
            continue
        result.append(CreateArticlesFromThisDirectory(article_id))
        article_id = len(result)
        os.chdir(currentwd)
    os.chdir("..")
    # save to Data Base
    SaveArticles(db_name, articles)


if __name__ == '__main__':
    #ClassifyArticles(to_compare)
    #CreateBdOfArticles('.','test_sample.db')
    ClassifyArticles('test_sample.db', 'data_bases/sci_articles.db')
#    total_word_prob_a = GetTotalWordProb('data_bases/sciAm2008-2011.db')
#    total_word_prob_b = GetTotalWordProb('data_bases/fiction.db')
