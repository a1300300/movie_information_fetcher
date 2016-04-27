# -*- coding: utf_8 -*-
from __future__ import division, unicode_literals
import os
import pandas as pd
import math
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from textblob_de import TextBlobDE as tb
bloblist = []
movielist = []
conjunction_list = ['AFTER', 'ALTHOUGH', 'AS', 'BECAUSE', 'BEFORE', 'BY', 'EVEN', 'IF', 'IN', 'LEST',
                    'ONCE', 'ONLY', 'PROVIDED', 'SINCE', 'SO', 'THAN', 'THAT', 'THOUGH', 'TILL',
                    'UNLESS', 'UNTIL', 'WHEN', 'WHENEVER', 'WHERE', 'WHEREVER', 'WHILE', 'BOTH', 'AND',
                    'EITHER', 'NEITHER', 'OR', 'NOR', 'NOT', 'ONLY', 'BUT', 'ALSO', 'WHETHER', 'TO',
                    'ARE', 'AM', 'IS', 'YOU', 'HE', 'HIS', 'HER', 'SHE', 'ME', 'MY', 'THE', 'WHO', 'AT', 'AND',
                    'WITH', 'THEY', 'THEIR']
column_names = [['First word', 'First score'], ['Second word', 'Second score'], ['Third word', 'Third score']]


def tf(word, blob):
    return blob.words.count(word) / len(blob.words)


def n_containing(word, bloblist):
    return sum(1 for blob in bloblist if word in blob)


def idf(word, bloblist):
    return math.log(len(bloblist) / (1 + n_containing(word, bloblist)))


def tfidf(word, blob, bloblist):
    return tf(word, blob) * idf(word, bloblist)


def calculate_text_value(plot_input_path, input_file, output_file):
    files = os.listdir(plot_input_path)
    movie_data = pd.read_csv(input_file)
    movie_data['First word'] = ''
    movie_data['First score'] = 0.0
    movie_data['Second word'] = ''
    movie_data['Second score'] = 0.0
    movie_data['Third word'] = ''
    movie_data['Third score'] = 0.0

    with open('./all_first_name.txt', 'r') as f1:
        first_name_source = f1.readlines()

    with open('./all_surname.txt', 'r') as f2:
        surname_source = f2.readlines()

    for file in files:
        movie_name = file.replace('.txt', '')
        source = tb(open(plot_input_path + file).read())
        bloblist.append(source)
        movielist.append(movie_name)

    for i in range(len(bloblist)):
        try:
            scores = {word: tfidf(word, bloblist[i], bloblist) for word in bloblist[i].words}
            sorted_words = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            word_count = 0
            word_list = []

            for word, score in sorted_words:
                if word_count < 3:
                    # if First char is Uppercase, it's possible the name
                    if 65 <= ord(word[0]) <= 90:
                        #check if first name
                        if check_if_name(first_name_source, word):
                            print 'Contain first name:' + word
                            continue
                        #check if surname
                        if check_if_name(surname_source, word):
                            print 'Contain surname:' + word
                            continue
                        #check if conjunction
                        if check_if_conj(conjunction_list, word):
                            print 'Contain conjunction:' + word
                            continue
                        #check if duplicate
                        if word.upper() in word_list:
                            print 'Duplicate word: ' + word
                            continue

                        #otherwise, add to list
                        print 'Add ' + str(word_count), word.upper() + ' to list'
                        movie_data.loc[i, column_names[word_count][0]] = word.upper()
                        movie_data.loc[i, column_names[word_count][1]] = score
                        word_list.append(word.upper())
                        word_count += 1
                        continue
                    #Not a name, only compare with conjunction
                    else:
                        #check if conjunction
                        if check_if_conj(conjunction_list, word):
                            print 'Contain conjunction:' + word
                            continue
                        #check if duplicate
                        if word.upper() in word_list:
                            print 'Duplicate word: ' + word
                            continue

                        #otherwise, add to list
                        print 'Add ' + str(word_count), word.upper() + ' to list'
                        movie_data.loc[i, column_names[word_count][0]] = word.upper()
                        movie_data.loc[i, column_names[word_count][1]] = score
                        word_list.append(word.upper())
                        word_count += 1
                        continue
                else:
                    break
            print word_list
            print ''

        except Exception as e:
            print str(e)

    movie_data = movie_data.sort_values('Release Date').set_index('Release Date')
    movie_data.to_csv(output_file)


def check_if_name(name_source, word):
    for i in name_source:
        name = i.replace('\n', '')
        if name[0] < word[0]:
            continue
        elif name[0] == word[0]:
            if len(name) == len(word) and name == word:
                return True
    return False


def check_if_conj(conjunction_list, word):
    if word.upper() in conjunction_list:
        return True
    return False

calculate_text_value('./IMDB_plot/', './movies_1990-2015_categorized.csv', './movies_1990-2015_categorized_token.csv')