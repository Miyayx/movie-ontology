#!/usr/bin/env python2.7
#encoding=utf-8

import codecs
import jieba
import marisa_trie

from model.query import Query
from model.little_entity import LittleEntity
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

        print "comment",self.comment
        for q in self.queries:
            print q
            print ""


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
        print "comment:",self.comment
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
            print q.text, q.index

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
                print "candidate", cans
                es_sim = Disambiguation(q.text, self.comment, cans).get_candidate()
                for e_id, sim in es_sim:
                    le = self.db.create_littleentity(e_id)
                    e = LittleEntity(**le)
                    e.sim = sim
                    q.entities.append(e)
            #else:
            #    self.queries.remove(q)

        #for q in self.queries:
        #    q.entity
        #    print q.entity.entity_id, q.entity.abstract

        #f.close()


def load_mention_entity(fn):
    m_e = {}

    for line in codecs.open(fn):
        line = line.strip("\n")
        m,es = line.split(":::")
        es = es.split("::;")
        m_e[m] = es[:-1]

    return m_e


if __name__=="__main__":
    trie = marisa_trie.Trie()
    trie.load('./data/m2e.trie')

    m_e = load_mention_entity("./data/mention.entity")

    db = MovieKB()

    #fw = codecs.open("data/result.dat","w",'utf-8')

    #with codecs.open("./data/评论1.txt", "r", "utf-8") as f:
    #    for c in f.readlines():
    #        c = c.strip("\n")
    #        movieel = MovieEL(c, trie, m_e)
    #        movieel.db = db
    #        movieel.run()

    #        fw.write("comment:"+c)
    #        fw.write("\n------------------------------------\n")
    #        for q in movieel.queries:
    #            fw.write(str(q).decode("utf-8"))
    #            fw.write("\n")
    #        fw.write("====================================\n")

    #fw.close()

    import os
    if not os.path.isdir("./data/comment-result"):
        os.mkdir("./data/comment-result")
    for name in os.listdir("./data/comment/"):
        fw = codecs.open("./data/comment-result/"+name, "w", "utf-8")
        with codecs.open("./data/comment/"+name, "r", "utf-8") as f:
            for c in f.readlines():
                if c.startswith(":::"):
                    c = c.strip("\n").strip(":::")
                    movieel = MovieEL(c, trie, m_e)
                    movieel.db = db
                    movieel.run()

                    fw.write("comment:"+c)
                    for q in movieel.queries:
                        fw.write(q.text+"\t")
                        for e in q.entities:
                            print e.sim
                            fw.write("%s,%s,%0.3f:::"%(e.id_, e.title.decode("utf-8"), e.sim))
                        fw.write("\n")
                    fw.write("====================================\n")

        fw.close()



    

