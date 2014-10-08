#!/usr/bin/python2.7
#-*-coding:utf-8-*-

import nltk
import string
import math

import jieba

from collections import Counter

from model.query import Query
from db import *

################# Strategy ####################
def context_sim(mention, cans, doc, db, num=0, threshold=None):
    """
    Compare context of comment and abstract of entity 
    """
    c_sim = {}
    
    def similar_cal(t, cans):
#         print ("candiates:" + ' '+candidates)
        for c in cans:
            print (c)
            a = db.get_abstract(c)
            if a:
                print (c+' ' +'has abstract')

                seg_list = jieba.cut(t, cut_all=False)
                t = " ".join(seg_list)
                seg_list = jieba.cut(a, cut_all=False)
                a = " ".join(seg_list)

                c_sim[c] = similarity(t, a)
                print ("similarity:")
                for k,v in c_sim.items():
                    print (k +' ' + str(v))
            else:
                c_sim[c] = 0.0

    def similarity(t1, t2):
        return Distance.cosine_distance(t1.lower(), t2.lower());
    #if len(self.candidates) == 1:
    #    return self.candidates[0]

    similar_cal(doc, cans)

    if threshold:
        for k,v in c_sim.items():
            if v < threshold:
                c_sim.popitem(k)

    return c_sim


class Disambiguation():

    def __init__(self, func=None, args = {}):

        if not func:
            raise ValueError("Not add strategy")
        self.func = func
        self.args = args

    def get_best(self):
        import operator
        c_sim = self.func(**self.args)
        best = max(c_sim.iteritems(), key=operator.itemgetter(1))
        print "best",best
        best = set(best)

    def get_sorted_cans(self, num=0):
        """
        Returns:
            return all candidate with their similarity
        """

        c_sim = self.func(**self.args)

        best = sorted(c_sim.items(), key=lambda x:x[1], reverse=True)
        if num:
            return best[:num]
        else:
            return best


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


