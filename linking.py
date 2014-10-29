#!/usr/bin/env python
#-*-coding=utf-8-*-

import codecs
import jieba
import marisa_trie
import re

import sys
reload(sys)
sys.setdefaultencoding('utf8')

from model.query import Query
from model.little_entity import LittleEntity
from disambiguation import *
from db import *
import json

PUNCT = set(u''':!),.:;?]}¢'"、。〉》」』】〕〗〞︰︱︳﹐､﹒
        ﹔﹕﹖﹗﹚﹜﹞！），．：；？｜｝︴︶︸︺︼︾﹀﹂﹄﹏､～￠
        々‖•·ˇˉ―--′’”([{£¥'"‵〈《「『【〔〖（［｛￡￥〝︵︷︹︻
        ︽︿﹁﹃﹙﹛﹝（｛“‘-—_…''')

PREFIX = 'http://keg.tsinghua.edu.cn/movie/'

class MovieEL():

    def __init__(self,comment, trie, can_set, db = None,movie_id = None,context = None ):
        self.movie_id = movie_id
        self.comment = comment
        self.context = context if context else comment 
        self.queries = []
        self.db = db
        self.trie = trie
        self.can_set = can_set
        self.full_mentions = None
        
    def destroy(self):
        del self.can_set
        del self.comment
        del self.context
        del self.db
        del self.queries
        del self.trie
        del self.movie_id


    def set_topic_mentions(self, mentions):
        self.full_mentions = mentions

    def run(self):
        mentions = self.extract_mentions(self.comment)
        for m in mentions:
            self.queries.append(Query(m[0],m[1]))
#         for q in self.queries:
#             print (q.text+' %d' % q.index)
        self.get_entity()
#         for q in self.queries:
# #             outputstr = "Text: %s,Index: %d\nEntity:%d" % (q.text.encode("utf-8"),q.index,q.entity)
# #             print(q.text), print(q.entity)
# #             print (q)
#             pass
      
    def word_segmentation(self, s):
        """
        Returns:
        seg_index: list of tuple, tuple(seg, place of this seg in s)
        """
        seg_list = jieba.cut(s, cut_all=False)
#         print (seg_list)
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

#         print ("comment:"+comment)
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
                            offset -= 1 #张江涛：逆向筛选时offset要回退，否则就会跳空分词
                            if t in self.trie:
                                #self.queries.append(Query(t, segs[i][1]))
                                mentions.append((t, segs[i][1]))
                                break
                        if len(s) > 0 and s[0] in PUNCT:#zjt:加入len(s) > 0的判断是有可能s为空
                            offset = 1 #如果字符串的第一个字是标点，可能会影响匹配结果，跳过标点再匹配
                    break
            i += offset
#         print(mentions)
        return mentions
    

    def get_entity(self):

#         if self.full_mentions:
#             con_mens = self.full_mentions
#         else:
#             con_mens = [q.text for q in self.queries]

        mentions = [q.text for q in self.queries]

        for q in self.queries:
            q.entities = []
            cans = self.can_set.get(q.text, [])
       
            q.candidates = cans
            cans = [c[1:-1].split("/")[-1] for c in cans]
            
            if cans:
#                 print ("candidate of " +q.text)

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
#                 args = {
#                         "context_mentions":con_mens,
#                         "mentions":mentions,
#                         "cans":cans,
#                         "mention":q.text,
#                         "db":self.db,
#                         "threshold":0.01
#                         }
#                 d = Disambiguation(entity_cooccur, args)

                ############# movie_related ###########
                args = {
                        "movie_id":self.movie_id,
                        "cans":cans,
                        "mention":q.text,
                        "context":self.comment,
                        "location":q.index,
                        "db":self.db,
                        "threshold":4
                        }
                d = Disambiguation(ranking, args)
 
                can_sim,c_info = d.get_sorted_cans(1) #top 3
#                 can_sim = d.get_best() #top 3

                for e_id, sim in can_sim:
#                     le = self.db.create_littleentity(e_id)
#                     e = LittleEntity(**le)
                    
                    uri = PREFIX + 'instance/' + e_id
                    title = c_info[e_id]
                    e = LittleEntity(e_id,uri,title,sim)
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
        fw = codecs.open(out_dir+name+"-thr4", "w", "utf-8")
        full_text = ""
        with codecs.open(in_dir+name, "r", "utf-8") as f:
            full_text = " ".join(f.readlines())
        mentions = [m[0] for m in MovieEL(full_text, trie, m_e).extract_mentions(full_text)]
        title =""
        movie_id = ""
        with codecs.open(in_dir+name, "r", "utf-8") as f:
            count = 0
            
            for c in f.readlines():
                if c.startswith("Title:"):
                    title = c.split(":::")[0][6:]
                    movie_id = c.split(":::")[1]
                    print("the title of movie commented is :" + title)
                    print("the id of movie commented is : "+ movie_id)
                if c.startswith(":::"):
                    count += 1

                    c = c.strip("\n").strip(":::")
                    movieel = MovieEL(c, trie, m_e, full_text)
                    movieel.db = db
                    movieel.movie_id = movie_id
                    movieel.full_mentions = mentions
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

def linking(in_dir, out_dir, fun=None):

    db = MovieKB()

    import os
    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)
    for name in os.listdir(in_dir):
        fw = codecs.open(out_dir+name+"-www-threshold4", "w", "utf-8")
        full_text = ""
        with codecs.open(in_dir+name, "r", "utf-8") as f:
            full_text = " ".join(f.readlines()).lower()
        mentions = [m[0] for m in MovieEL(full_text, trie, m_e).extract_mentions(full_text)]
        title =""
        movie_id = ""
        comm_list = full_text.split('::::')
        
#         with codecs.open(in_dir+name, "r", "utf-8") as f:
#             count = 0
        count = 0
        for c in comm_list:
            if c.startswith("title:"):
                title = c.split(":::")[0][6:]
                movie_id = c.split(":::")[1]
                print("the title of movie commented is :" + title)
                print("the id of movie commented is : "+ movie_id)
            else:
                count += 1

                c = c.strip("\n")
                movieel = MovieEL(c, trie, m_e, full_text)
                movieel.db = db
                movieel.movie_id = movie_id
                movieel.full_mentions = mentions
                movieel.run()

                print ("Num of queries(mentions):%d"%len(movieel.queries))
                for q in movieel.queries:
                    if len(q.entities) > 0:
                        for e in q.entities:
                            print (q.text+","+e.title+":"+str(e.sim))
			    #output = {u"lineNum":count,u"mention":q.text,"location":q.index,"uri":e.uri,"title":e.title}
			    #outputput = [count,q.text,q.index,q.index+len(q.text), e.uri,e.title]
			    #output += e.sim
		 	    
                            fw.write("%d:::%s:::%d:::%d;;;%s:::%s:::("%(count, q.text, q.index, q.index+len(q.text), e.uri, e.title))
                            for item in e.sim:
                                fw.write('(' + item + ') ')
                            fw.write(')')
                            fw.write('\n')
                    #else:
                    #    fw.write("%d:::%s:::%d:::%d;;;"%(count, q.text, q.index, q.index+len(q.text)))

                #fw.write("====================================\n")
                fw.write("\n")

        fw.close()

    db.close()
    
    
    
def linking2(in_dir, out_dir,trie, m_e,fun=None):

    db = MovieKB()

    import os
    
    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)
        

        
    for sub_dir in os.listdir(in_dir):
        if not os.path.isdir(out_dir + sub_dir ):
            os.mkdir(out_dir + sub_dir)
        pair = sub_dir.split('-')
        if len(pair) < 2:
            continue
        title = pair[0]
        movie_id = pair[1]
        print(title)
        print(movie_id)
        for name in os.listdir(in_dir + sub_dir):             
            fw = codecs.open(out_dir+sub_dir+'/' +name + 'threshold4', 'w', "utf-8")
            full_text = ""
            fi = codecs.open(in_dir+sub_dir+'/' +name, 'r', "utf-8")
            count = 0
            total_mentions = 0
            print("current article is :  "+in_dir+sub_dir+'/' +name)
            for line in  fi :
                
                if "{" in line and "content" in line:
                    
                    main = line[line.find("{"):]
                    try:
                        comment_dict = json.loads(main)
                        c = comment_dict["content"].lower()
                    except:
                        print("error line: " +line)
                        continue
    
                    count += 1
        
                    c = c.strip("\n")
                    movieel = MovieEL(c, trie, m_e,db,movie_id)
                    movieel.run()
                    print("the line number is : %d and number of queries(mentions):%d"%(count,len(movieel.queries)))
#                     print ("Num of queries(mentions):%d"%len(movieel.queries))
                    for q in movieel.queries:
                        if len(q.entities) > 0:
                            total_mentions += 1
                            for e in q.entities:
#                                 print (q.text+","+e.title+":"+str(e.sim))
#                                 fw.write("%d:::%s:::%d:::%d;;;%s:::%s:::("%(count, q.text, q.index, q.index+len(q.text), e.uri, e.title))
                                fw.write('{"comment_id":%d,"mention":"%s","pos":%d,"uri":"%s","title":"%s"}:::('%(count, q.text, q.index, e.uri, e.title))
                                for s in e.sim:
                                    fw.write('[')
                                    if type(s) == type(1):
                                        fw.write('%d'%s)
                                    if type(s) == type(set()):
                                        for item in s:
                                            fw.write(str(item) + ', ')
                                    fw.write('], ')
                                fw.write(')')
                                fw.write('\n')
                        #else:
                        #    fw.write("%d:::%s:::%d:::%d;;;"%(count, q.text, q.index, q.index+len(q.text)))
        
                    #fw.write("====================================\n")
    #                 fw.write("\n")
    
    #                 fw.write("\n")
            print("the total mentions of this comment are : %d"%total_mentions)
            fw.write("the total mentions of this comment are : %d"%total_mentions )
            fw.close()
            fi.close()
            movieel.destroy()
            del movieel
            
    db.close()
    
if __name__=="__main__":

    trie = marisa_trie.Trie()
    trie.load('./data/m2e.trie')
    #result = trie.keys(u'冯绍峰')
    #print(result)
    m_e = load_mention_entity("./data/mention.entity_www")
#     linking("./data/test/","./data/test-fulltext-thre-result/")
#     linking2("./data/test/","./data/test-fulltext-thre-result/")
    linking2("./data/input/","./data/output/",trie, m_e)
    
#     s = u"看这片之前要先看完《时间简史》，看完这片有助于理解《时间简史》，那先看哪个好呢？能把传统和现代、守旧与创新、严肃与浪漫这样结合的，也只有英国人做得到了。费劲巴啦地解释了多少条命的问题，其实就是为了换主角呗。新任博士为什么一出场就说肾的问题呢？他穿来穿去地爽，那女主角要不要老去呢？"
#     movieel = MovieEL(s,trie,m_e)
# #     print(movieel.word_segmentation(s))
#     print(movieel.extract_mentions(s))
#     c = u"""讨厌 就怕别人被带入新剧角色叫你阿加西是不是嘛//@娜女生唯爱郑萌萌智薰大哥: 他这么自恋无尽头的人，果然憋不住了快乐大本营和电影宣传的时候，使劲喊oppa吧 //@smile_雨中倾听:哈哈。。对于我们来说就是偶吧。。偶吧。。 //@被郑小贱贱晕的门儿:。。。强调自己是欧巴//"""
#     m_el = movieel = MovieEL(c, trie, m_e)
#     m_el.extract_mentions(c)
    
   
    
    
    
    
    
    
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
    
    
    #test_run("./data/new-comment/","./data/new_comment-fulltext-result/")
    #test_run("./data/new-comment/","./data/new_comment-fulltext-thre-result/")
