#!/usr/bin/env python
#-*-coding:utf-8-*-

import pyodbc
import codecs
from urllib import *

from utils import *
from symbol import except_clause
from virtdb import *

PREFIX = 'http://keg.tsinghua.edu.cn/movie/'
GRAPH = 'keg-movie2'
#SERVER_URL = 'http://localhost:5678/query'
SERVER_URL = 'http://10.1.1.23:5678/query'

class MovieKB():
    """
    Properties
    --------------------------
    """
    
    def __init__(self):
        configs = ConfigTool.parse_config("./config/db.cfg","MovieKB")
        import sys
        if sys.platform == 'linux':
            #self.db = JenaVirtDB(**configs)
            #self.db = OdbcVirtDB(**configs)
            self.db = HttpDB(**configs)
        else:
            #self.db = JenaVirtDB(**configs)
            configs["prefix"] = PREFIX
            configs["url"] = SERVER_URL
            self.db = HttpDB(**configs)

    def close(self):
        self.db.close()

    def fetch_one_result(self, sq):
        """
        Fetch one result from xlore virtuoso database according to query the sq string

        return:
            one result(if hits) or None(if no hit)
        """
        cursor = self._virtodb.cursor()
        results = cursor.execute(sq)
        try:
            result = results.fetchone()[0]
            if type(result) == tuple:
                result = result[0]
        except TypeError:
            return None
        finally:
            cursor.close()
        return result

    def fetch_multi_result(self, sq):
        """
        Fetch multi results from xlore virtuoso database according to query the sq string

        return:
            result list(if hits) or empty list(if no hit)
        """
        cursor = self._virtodb.cursor()
        try:
            results = [r[0] for r in cursor.execute(sq).fetchall()]
            if results and len(results) > 0 and type(results[0]) == tuple:
                results = [r[0] for r in results]
        except TypeError:
            return []
        finally:
            cursor.close()
        return results

    def get_instance_properties(self, entity_id):
        """
        Returns:
        result:dict
            k: shortcomming of property
            v: list of object
        """
        sq = 'select * from <%s> where {<%sinstance/%s> ?p ?o}'%(GRAPH, PREFIX,entity_id)
        result_set = self.db.query(sq)
        result = {}
        for p, o in result_set:
            result[p] = result.get(p,[]) + [o]
        return result

    def parse_properties(self, p2o):

        result = {}

        for p,o in p2o.items():
            key = p.split("/",5)[-1]
            result[key] = o

        return result
    
    def get_whole_info_label (self,entity_id):
        """
                            返回该实体的结构化信息p2o，
                key为该实体的属性名（去掉前缀，保留/分割的第5个部分）
                value为该属性值（若为对象型属性，则替换为该对象的label）
        """
        q_result = self.get_instance_properties(entity_id)
        p2o = self.parse_properties(q_result)
        for p in p2o:
            for obj in p2o[p]:
                if obj.startswith(PREFIX):
                    if p != 'actor_list' :
                        label = self.get_label_uri(obj)
                    else: label = self.get_bb_label_uri(obj)
                    p2o[p][p2o[p].index(obj)] = label
        return p2o
    
    def get_whole_info (self,entity_id):
        """
                            返回该实体的结构化信息p2o，
                key为该实体的属性名（去掉前缀，保留/分割的第5个部分）
                value为该属性值（若为对象型属性，则替换为该对象的label）
        """
        q_result = self.get_instance_properties(entity_id)
        p2o = self.parse_properties(q_result)
        for p in p2o:
            if p == 'actor_list' :
                for obj in p2o[p]:
                    if obj.startswith(PREFIX):   
                                        
                        id = self.get_bb_obj_uri(obj).split("/")[-1]
                        
                        p2o[p][p2o[p].index(obj)] = id

        return p2o
    
    def extract_mention_in_body(self, entity_id):
        """
                    从summary和description中提取[[]]之间的实体内容
        """
        q_result = self.get_instance_properties(entity_id)
        p2o = self.parse_properties(q_result)
        print(p2o)
        s = set()
        t = ""
        for string in p2o["description/zh"]:#注意value是list形式的
            while True:
                if "[[" in string and "]]" in string:
                    start = string.index("[[") + 2
                    end = string.index("]]", start) 
                    t = string[start:end]
                    s.add(t.split("||")[0])
                    string = string[end:]
                else: break
        t = ""        
        for string in p2o["summary"]:#注意value是list形式的
            while True:
                if "[[" in string and "]]" in string:
                    start = string.index("[[") + 2
                    end = string.index("]]", start) 
                    t = string[start:end]
                    s.add(t.split("||")[0])
                    string = string[end:]
                else: break

        return s
        
    def get_prop_entities(self, entity_id):

        def deep_instance(d, p):
            """
            获取instance地址下的label
            """
            s = set()
            if p in d.keys():
                for e in d[p]:#注意value是list形式的
                    if e.startswith(PREFIX):
                        i = e.split("/")[-1]
                        l = self.get_label(i)
                        if not l:
                            return s
                        if "[" in l:
                            s.add(l[:l.index("[")])
                        else: s.add(l)
                    else: s.add(e)
            return s
        
        def deep_blankNode(d, p):
            """
            获取blank node地址下的label
            """
            s = set()
            if p in d.keys():
                for e in d[p]:#注意value是list形式的
                    
                    if e.startswith(PREFIX):
#                         print("debug :" + e)
                        i = e.split("/")[-1]
                        l = self.get_bb_label(i)
                        if not l:
                            return s
                        if "[" in l:
                            s.add(l[:l.index("[")])
                        else: s.add(l)
                    else: s.add(e)
            return s

        def deep_concept(d, p):
            """
            获取concept地址下的label
            """
            s = set()
            if p in d.keys():
                for e in d[p]: #注意value是list形式的
                    if e.startswith(PREFIX):
                        i = e.split("/")[-1]
                        l = self.get_concept_label(i)
                        if not l:
                            return s
                        if "[" in l:
                            s.add(l[:l.index("[")])
                        else: s.add(l)
                    else: s.add(e)
            return s

        def extract_ins(d, p):
            """
            从summary和description中提取[[]]之间的实体内容
            """
            s = set()
            t = ""
            if p in d.keys():
                for string in d[p]:#注意value是list形式的
                    while True:
                        if "[[" in string and "]]" in string:
                            start = string.index("[[") + 2
                            end = string.index("]]", start) 
                            t = string[start:end]
                            s.add(t.split("||")[0])
                            string = string[end:]
                        else: break

            return s

        q_result = self.get_instance_properties(entity_id)
        d = self.parse_properties(q_result)

        es = set()
        #不能有label啊，不然肯定有共现的词
        #es.add(d["label/zh"][0])

        if not "label/zh" in d.keys():
        #连label都没有。。。扔掉！
            return es
  
        if "alias" in d.keys():
            es = es.union(set(d["alias"]))
        es = es.union(deep_concept(d, "instanceOf"))
        # For movie
        es = es.union(deep_instance(d,"directed_by"))
        es = es.union(deep_instance(d,"written_by"))
        es = es.union(deep_blankNode(d,"actor_list"))
        # For actor
        es = es.union(deep_instance(d,"work_list"))
        es = es.union(deep_instance(d,"profession/zh"))
        es = es.union(extract_ins(d, "summary"))
        es = es.union(extract_ins(d, "description/zh"))

        return es


    def get_abstract(self, entity_id):
        #sq = 'select * from <%s> where {<%sinstance/%s> <%scommon/summary> ?o }'%(GRAPH, PREFIX, entity_id, PREFIX)
        sq = 'select * from <%s> where {<%sinstance/%s> ?p ?o}'%(GRAPH, PREFIX,entity_id)
        result_set = self.db.query(sq)
        for p, o in result_set:
            if p.endswith('common/summary'):
                return o

        #return self.fetch_one_result(sq)

    def get_label(self, entity_id):
        #sq = 'select * from <%s> where {<%sinstance/%s> <%scommon/summary> ?o }'%(GRAPH, PREFIX, entity_id, PREFIX)
        sq = 'select * from <%s> where {<%sinstance/%s> ?p ?o}'%(GRAPH, PREFIX,entity_id)
        result_set = self.db.query(sq)
        for p, o in result_set:
            if p.endswith('label/zh'):
                return o
    
    def get_label_uri(self, uri):
        """
                        用uri而不是id获取label
        """
        #sq = 'select * from <%s> where {<%sinstance/%s> <%scommon/summary> ?o }'%(GRAPH, PREFIX, entity_id, PREFIX)
        sq = 'select * from <%s> where {<%s> ?p ?o}'%(GRAPH, uri)
        result_set = self.db.query(sq)
        for p, o in result_set:
            if p.endswith('label/zh'):
                return o
            
    def get_bb_label(self, entity_id):
        """
                         获取blank node的label
        """
        #sq = 'select * from <%s> where {<%sinstance/%s> <%scommon/summary> ?o }'%(GRAPH, PREFIX, entity_id, PREFIX)
        sq = 'select * from <%s> where {<%sinstance/%s> ?p ?o}'%(GRAPH, PREFIX,entity_id)
        result_set = self.db.query(sq)
        for p, o in result_set:
            if p.endswith('actor_name'):
                return o
            
    def get_bb_label_uri(self, uri):
        """
                        用uri而不是id获取blank node 的label
        """
        #sq = 'select * from <%s> where {<%sinstance/%s> <%scommon/summary> ?o }'%(GRAPH, PREFIX, entity_id, PREFIX)
        sq = 'select * from <%s> where {<%s> ?p ?o}'%(GRAPH, uri)
        result_set = self.db.query(sq)
        for p, o in result_set:
            if p.endswith('actor_name'):
                return o
            
    def get_bb_obj_uri(self, uri):
        """
                        用uri而不是id获取blank node 的label
        """
        #sq = 'select * from <%s> where {<%sinstance/%s> <%scommon/summary> ?o }'%(GRAPH, PREFIX, entity_id, PREFIX)
        sq = 'select * from <%s> where {<%s> ?p ?o}'%(GRAPH, uri)
        result_set = self.db.query(sq)
        for p, o in result_set:
            if p.endswith('actor_id'):
                return o

    def get_concept_label(self, entity_id):
#         sq = 'select * from <%s> where {<%sinstance/%s> ?p ?o}'%(GRAPH, PREFIX,entity_id)
        sq = 'select * from <%s> where {<%sconcept/%s> ?p ?o}'%(GRAPH, PREFIX,entity_id)
        result_set = self.db.query(sq)
        for p, o in result_set:
            if p.endswith('label/zh'):
                return o

    def create_littleentity(self, entity_id):
            
        entity = {}
        entity_id = str(entity_id)
        entity["id_"] = entity_id
        entity["uri"] = PREFIX+entity_id

        q_result = self.get_instance_properties(entity_id)

        d = self.parse_properties(q_result)

        entity["title"] = d["label/zh"][0]
#         if d.has_key("alias"):
        if "alias" in d:
            entity["alias"] = d["alias"]
#         if d.has_key("summary"):
        if "summary" in d:
            entity["abstract"] = d["summary"][0]
#         if d.has_key("firstimage"):
        if "firstimage" in d:
            entity["image"] = d["firstimage"][0]

        return entity

if __name__ == "__main__":
    configs = ConfigTool.parse_config("./config/db.cfg","MovieKB")
    mkb = MovieKB()
#     print(mkb.get_prop_entities("dt10063708"))
    print(mkb.get_whole_info("dt10063708"))
    print(mkb.get_whole_info("dt10082480"))

