#!/usr/bin/env python2.7
#encoding=utf-8

import codecs
import jieba
import marisa_trie
import re

from model.query import Query
from disambiguation import *
from db import *

class MovieEL():

    def __init__(self, comment, trie, can_set):
        self.comment = comment
        self.queries = []
        self.db = None
        self.trie = trie
        self.can_set = can_set

    def run(self):
        self.extract_mentions()
        self.get_entity()
        for q in self.queries:
            print (q)
            print (q.entity["title"])
            print (q.entity["abstract"])
        

    def word_segmentation(self, s):
        """
        Returns:
        seg_index: list of tuple, tuple(seg, place of this seg in s)
        """
        seg_list = jieba.cut(s, cut_all=False)
        seg_index = []
        last = 0
        for seg in seg_list:
            seg = seg.strip("/")
            begin = s.index(seg, last)
            last = begin + len(seg)
            seg_index.append((seg, begin))
    
        return seg_index
    
    def extract_mentions(self):
        print ("comment:"+self.comment)
        segs = self.word_segmentation(self.comment)
    
        i = 0
        while i < len(segs):
            offset = 1
            temp = []
            while True:
                s = "".join([seg[0] for seg in segs[i:i+offset]])
                if len(self.trie.keys(s)) > 0:# s is prefix or word 
                    temp.append(s)
                    offset += 1
                else: # not prefix or word, search end
                    if len(temp) > 0:
                        temp.reverse()
                        for t in temp:
                            if t in self.trie:
                                self.queries.append(Query(t, segs[i][1]))
                                break
                    break
            i += offset
    
        for q in self.queries:
            print (q.text+' '+ q.index)

    def get_entity(self):

        #f = codecs.open("./data/mentions.dat", "w","utf-8")
        for q in self.queries:
            cans = self.can_set.get(q.text.encode("utf-8"), [])
            q.candidates = cans
            cans = [c[1:-1].split("/")[-1] for c in cans]
            #print q.text, q.candidates
            #s = q.text+":::"+";;;".join(q.candidates)
            #f.write(s+"\n")
            if cans:
                print ("candidate" +' ' +cans)
                q.entity_id = Disambiguation(q.text, self.comment, cans).get_best()
                le = self.db.create_littleentity(q.entity_id)
                #q.entity = LittleEntity(**le)
                q.entity = le
            else:
                self.queries.remove(q)

        #for q in self.queries:
        #    q.entity
        #    print q.entity.entity_id, q.entity.abstract

        #f.close()


def load_mention_entity(fn):
    m_e = {}
    fi =codecs.open(fn,'r',"utf-8")
    for line in fi:
#         line = line.strip()
#         m,es = line.split(":::")
        m,es = re.split(":::",line.strip("\n"))
        es = es.split("::;")
        m_e[m] = es[:-1]

    return m_e


if __name__=="__main__":
    trie = marisa_trie.Trie()
    trie.load('./data/m2e.trie')

    m_e = load_mention_entity("./data/mention.entity")

    db = MovieKB()

    with codecs.open("./data/评论.txt", "r", "utf-8") as f:
        c = f.readline().strip("\n")
        movieel = MovieEL(c, trie, m_e)
        movieel.db = db
        movieel.run()
    

