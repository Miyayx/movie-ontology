#!/usr/bin/python2.7
#-*-coding:utf-8-*-

import nltk
import string
import math

import jieba

from collections import Counter

from model.query import Query
from db import *

class Disambiguation():

    def __init__(self, m, d, candidates):
        self.mention = m
        self.doc = d
        self.candidates = candidates
        self.c_sim = {}
        self.threshold = 0.9

    def get_best_use_title(self, num = 0):
        """
        Calculate the edit distance between two titles and get the most similar ones
        """

        if len(self.candidates) == 1:
            print ("Has only one candidates ")
            return self.candidates

        for c in self.candidates:
            t = Xlore().get_en_title(c)
            self.c_sim[c] = Distance.levenshtein(self.doc, t)

        import operator
        if num <= 1 or not num:
            best = min(self.c_sim.iteritems(), key=operator.itemgetter(1))[0]
            
        else:
            best = sorted(self.c_sim.keys(), key=self.c_sim.get)[:num]
        return best

    def get_best(self, num = 0):
        if len(self.candidates) == 1:
            return self.candidates[0]

        self.similar_cal(self.doc, self.candidates)

        import operator
        if num <= 1 or not num:
            best = max(self.c_sim.iteritems(), key=operator.itemgetter(1))[0]
            
        else:
            best = max(self.c_sim.iteritems(), key=operator.itemgetter(1))[:num]
        return best

    def similar_cal(self, t, candidates):
        print ("candiates:" + ' '+candidates)
        for c in candidates:
            print (c)
            a = MovieKB().get_abstract(c)
            if a:
                print (c,+' ' +"has abstract")

                seg_list = jieba.cut(t, cut_all=False)
                t = " ".join(seg_list)
                seg_list = jieba.cut(a, cut_all=False)
                a = " ".join(seg_list)

                self.c_sim[c] = self.similarity(t, a)
                print ("similarity:")
                for k,v in self.c_sim.items():
                    print (k +' ' + v)
            else:
                self.c_sim[c] = None

    def similarity(self, t1, t2):
        return Distance.cosine_distance(t1.lower(), t2.lower());


class Distance():

    @staticmethod
    def cosine_distance(t1, t2):
        """
        Return the cosine distance between two strings
        """

        def cosine(u, v):
            """
            Returns the cosine of the angle between vectors v and u. This is equal to u.v / |u||v|.
            """
            import numpy
            import math
            return numpy.dot(u, v) / (math.sqrt(numpy.dot(u, u)) * math.sqrt(numpy.dot(v, v)))

        tp = TextProcesser()
        c1 = dict(tp.get_count(t1))
        c2 = dict(tp.get_count(t2))
        keys = c1.keys() + c2.keys()
        word_set = set(keys)
        words = list(word_set)
        v1 = [c1.get(w,0) for w in words]
        v2 = [c2.get(w,0) for w in words]
        return cosine(v1, v2)

    @staticmethod
    def levenshtein(first, second):
        """
        Edit Distance
        """
        if len(first) > len(second):
            first,second = second,first
        if len(first) == 0:
            return len(second)
        if len(second) == 0:
            return len(first)
        first_length = len(first) + 1
        second_length = len(second) + 1
        distance_matrix = [range(second_length) for x in range(first_length)]
        #print distance_matrix 
        for i in range(1,first_length):
            for j in range(1,second_length):
                deletion = distance_matrix[i-1][j] + 1
                insertion = distance_matrix[i][j-1] + 1
                substitution = distance_matrix[i-1][j-1]
                if first[i-1] != second[j-1]:
                    substitution += 1
                distance_matrix[i][j] = min(insertion,deletion,substitution)
        return distance_matrix[first_length-1][second_length-1]


class TextProcesser():

    def __init__(self):
        pass

    def get_tokens(self, t):
        lowers = t.lower()
        #remove the punctuation using the character deletion step of translate
        #no_punctuation = lowers.translate(None, string.punctuation)
        no_punctuation = lowers.translate(string.punctuation)
        tokens = nltk.word_tokenize(no_punctuation)
        from nltk.corpus import stopwords
        tokens = [w for w in tokens if not w in stopwords.words('english')]
        return tokens

    def stem_tokens(self, tokens, stemmer):
        stemmed = []
        for item in tokens:
            stemmed.append(stemmer.stem(item))
        return stemmed

    def get_count(self, t):
        return Counter(self.get_tokens(t)).most_common()


