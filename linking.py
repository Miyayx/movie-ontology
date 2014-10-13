#!/usr/bin/env python
#-*-coding=utf-8-*-

import codecs
import jieba
import marisa_trie
import re

from model.query import Query
from model.little_entity import LittleEntity
from disambiguation import *
from db import *

PUNCT = set(u''':!),.:;?]}¢'"、。〉》」』】〕〗〞︰︱︳﹐､﹒
        ﹔﹕﹖﹗﹚﹜﹞！），．：；？｜｝︴︶︸︺︼︾﹀﹂﹄﹏､～￠
        々‖•·ˇˉ―--′’”([{£¥'"‵〈《「『【〔〖（［｛￡￥〝︵︷︹︻
        ︽︿﹁﹃﹙﹛﹝（｛“‘-—_…''')

class MovieEL():

    def __init__(self, comment, trie, can_set, context = None ):
        self.comment = comment
        self.context = context if context else comment 
        self.queries = []
        self.db = None
        self.trie = trie
        self.can_set = can_set
        self.full_mentions = None

    def set_topic_mentions(self, mentions):
        self.full_mentions = mentions

    def run(self):
        mentions = self.extract_mentions(self.comment)
        for m in mentions:
            self.queries.append(Query(m[0],m[1]))
        for q in self.queries:
            print (q.text+' %d' % q.index)
        self.get_entity()
        for q in self.queries:
#             outputstr = "Text: %s,Index: %d\nEntity:%d" % (q.text.encode("utf-8"),q.index,q.entity)
#             print(q.text), print(q.entity)
#             print (q)
            pass
      
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
            #print re.split('(《》)', seg)[0]
            begin = s.index(seg, last)
            last = begin + len(seg)
            seg_index.append((seg, begin))
    
        return seg_index
    
    def extract_mentions(self, comment):
        """
        Extract mentions from comment
        正向最大匹配中文分词算法
        http://hxraid.iteye.com/blog/667134
        """

        mentions = []

        print ("comment:"+comment)
        segs = self.word_segmentation(comment)
    
        i = 0
        while i < len(segs):
            offset = 1
            temp = []
            while True:
                s = "".join([seg[0] for seg in segs[i:i+offset]])
                if len(self.trie.keys(s)) > 0 and i+offset < len(segs):# s is prefix or word 
                    temp.append(s) #把可能在tree里找到的都存起来,如： a, aa, aaa 
                    offset += 1
                else: # not prefix or word, search end
                    if len(temp) > 0:
                        temp.reverse() #从最长的字符串开始查找，看是不是在tree里,如果有，就结束查找，生成Query，这部分的遍历就结束了,如：如果有aaa，那aaa就是要找的字符串，aa和a都不要
                        for t in temp:
                            if t in self.trie:
                                #self.queries.append(Query(t, segs[i][1]))
                                mentions.append((t, segs[i][1]))
                                break
                        if s[0] in PUNCT:
                            offset = 1 #如果字符串的第一个字是标点，可能会影响匹配结果，跳过标点再匹配
                    break
            i += offset

        return mentions
    

    def get_entity(self):

        if self.full_mentions:
            con_mens = self.full_mentions
        else:
            con_mens = [q.text for q in self.queries]

        mentions = [q.text for q in self.queries]

        for q in self.queries:
            q.entities = []
            cans = self.can_set.get(q.text, [])
       
            q.candidates = cans
            cans = [c[1:-1].split("/")[-1] for c in cans]
            
            if cans:
                print ("candidate of " +q.text)

                ####### context_sim ##########
#                 args = {
#                         "mention" : q.text, 
#                         "cans": cans, 
#                         "doc" : self.comment,
#                         "db"  : self.db,
#                         "threshold":None
#                         }
# 
#                 d = Disambiguation(context_sim, args)

                ############# entity_cooccur ###########
                args = {
                        "context_mentions":con_mens,
                        "mentions":mentions,
                        "cans":cans,
                        "mention":q.text,
                        "db":self.db,
                        "threshold":0.01
                        }
                d = Disambiguation(entity_cooccur, args)
 
                can_sim = d.get_sorted_cans(num=3) #top 3
#                 can_sim = d.get_best() #top 3

                for e_id, sim in can_sim:
                    le = self.db.create_littleentity(e_id)
                    e = LittleEntity(**le)
                    e.sim = sim
                    q.entities.append(e)
            #else:
            #    self.queries.remove(q)


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

def test_run(in_dir, out_dir, fun=None):

    db = MovieKB()

    import os
    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)
    for name in os.listdir(in_dir):
        fw = codecs.open(out_dir+name+"-sim", "w", "utf-8")
        full_text = ""
        with codecs.open(in_dir+name, "r", "utf-8") as f:
            full_text = " ".join(f.readlines())
        mentions = [m[0] for m in MovieEL(full_text, trie, m_e).extract_mentions(full_text)]
        with codecs.open(in_dir+name, "r", "utf-8") as f:
            count = 0
            for c in f.readlines():
                if c.startswith(":::"):
                    count += 1

                    c = c.strip("\n").strip(":::")
                    movieel = MovieEL(c, trie, m_e, full_text)
                    movieel.db = db
                    movieel.set_topic_mentions(mentions)
                    movieel.run()

                    print ("Num of queries(mentions):%d"%len(movieel.queries))
                    for q in movieel.queries:
                        if len(q.entities) > 0:
                            for e in q.entities:
                                print (q.text+","+e.title+":"+str(e.sim))
                                fw.write("%d:::%s:::%d:::%d;;;%s:::%s:::%0.5f\n"%(count, q.text, q.index, q.index+len(q.text), e.uri, e.title, e.sim))
                        #else:
                        #    fw.write("%d:::%s:::%d:::%d;;;"%(count, q.text, q.index, q.index+len(q.text)))

                    #fw.write("====================================\n")
                    fw.write("\n")

        fw.close()

    db.close()


if __name__=="__main__":

    trie = marisa_trie.Trie()
    trie.load('./data/m2e.trie')

    m_e = load_mention_entity("./data/mention.entity")

    #db = MovieKB()

    #fw = codecs.open("./data/test-sent/1.result","w",'utf-8')
    #with codecs.open("./data/test-sent/1","r","utf-8") as f:
    #    for c in f.readlines():
    #        c = c.strip("\n")
    #        movieel = MovieEL(c, trie, m_e)
    #        movieel.db = db
    #        movieel.run()

    #        fw.write("comment:"+c)
    #        fw.write("\n------------------------------------\n")
    #        for q in movieel.queries:
    #            if len(q.entities) > 0:
    #                for e in q.entities:
    #                    print (q.text+"\t"+e.title+":"+str(e.sim))
    #                    fw.write (q.text+"\t"+e.title+":"+str(e.sim)+"\n")
    #            else: fw.write(q.text+"\n")
    #        fw.write("====================================\n")

    #fw.close()


    #with codecs.open("./data/评论2.txt", "r", "utf-8") as f:
    #    for c in f.readlines():
    #        c = c.strip("\n")
    #        movieel = MovieEL(c, trie, m_e)
    #        movieel.db = db
    #        movieel.run()
    

    #test_run("./data/comment/","./data/comment-result/")
    #test_run("./data/test/","./data/test-result/")
    #test_run("./data/test-sent/","./data/test-sent-result/")
    test_run("./data/test/","./data/test-fulltext-thre-result/")
    
    #test_run("./data/new-comment/","./data/new_comment-fulltext-result/")
    #test_run("./data/new-comment/","./data/new_comment-fulltext-thre-result/")
