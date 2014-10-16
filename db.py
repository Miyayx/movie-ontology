#!/usr/bin/env python
#-*-coding:utf-8-*-

import pyodbc
import codecs
import json
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
        if re.match('linux',sys.platform):#Linux
            #self.db = JenaVirtDB(**configs)
            #self.db = OdbcVirtDB(**configs)
            configs["prefix"] = PREFIX
            configs["url"] = SERVER_URL
            self.db = HttpDB(**configs)
        else:#Windows
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

    def get_prop_entities(self, entity_id):

        def deep_instance(d, p):
            """
            获取instance地址下的label
            """
            s = set()
            if d.has_key(p):
                for e in d[p]:#注意value是list形式的
                    if e.startswith("http"):
                        i = e.split("/")[-1]
                        l = self.get_label(i)
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
            if d.has_key(p):
                for e in d[p]: #注意value是list形式的
                    if e.startswith("http"):
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
            if d.has_key(p):
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

        if not d.has_key("label/zh"):
            #连label都没有。。。扔掉！
            return es

        if d.has_key("alias"):
            es = es.union(set(d["alias"]))
        es = es.union(deep_concept(d, "instanceOf"))
        # For movie
        es = es.union(deep_instance(d,"directed_by"))
        es = es.union(deep_instance(d,"written_by"))
        es = es.union(deep_instance(d,"actor_list"))
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

    def get_concept_label(self, entity_id):
        sq = 'select * from <%s> where {<%sinstance/%s> ?p ?o}'%(GRAPH, PREFIX,entity_id)
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
        if d.has_key("alias"):
            entity["alias"] = d["alias"]
        if d.has_key("summary"):
            entity["abstract"] = d["summary"][0]
        if d.has_key("firstimage"):
            entity["image"] = d["firstimage"][0]

        return entity

    def get_entity_label(self, entity_id):
        sq = 'select * from <%s> where { <%s> <%sobject/label/zh> ?o }'%(GRAPH, entity_id, PREFIX)
        sq = 'select * from <%s> where {<%s> ?p ?o}'%(GRAPH, entity_id)
        print sq
        result_set = self.db.query(sq)
        for p, o in result_set:
            if p.endswith('label/zh'):
                return o


    def get_actor_info(self, actor_id):
        sq = 'select * from <%s> where {%s ?p ?o}'%(GRAPH, PREFIX,actor_id)
        #print sq
        result_set = self.db.query(sq)
        for p,o in result_set:
            pname = p
            return o

    def get_entity_info(self,entity_id):
        # 返回json数据
        predictmap = getPropMap()
        def get_baseinfo(entity_id,predictmap):
            result = {}
            objects= {}
            sq = 'select * from <%s> where {<%sinstance/%s> ?p ?o}'%(GRAPH, PREFIX,entity_id)
            result_set = self.db.query(sq)
            for p, o in result_set:
                #print p,o
                p = "<%s>"%p
                if p in  predictmap['objectType']:
                    pname = predictmap['objectType'][p]
                    if pname not in result:
                        result[pname] = []

                    if o.startswith(PREFIX):
                        #uid = "<%s>"%o
                        #name= self.get_entity_label(uid)
                        #result[pname].append({'id':uid,'name':name})
                        if pname not in objects: objects[pname]=[]
                        objects[pname].append(o)
                    else:
                        name= o
                        result[pname].append({'name':name})
                elif p in predictmap['dataType']:
                    pname = predictmap['dataType'][p]
                    if pname not in result: result[pname] = []
                    result[pname].append(o)
            return result,objects

        result,objects = get_baseinfo(entity_id,predictmap)

        def get_objectinfo(baseinfo,objects):
            result = baseinfo
            #处理objectType信息
            for pname in objects:
                if pname == u'演员表':
                    actor_info = [{} for i in range(len(objects[u'演员表']))]
                    for uid in objects[u'演员表']:
                        sq = 'select * from <%s> where {<%s> ?p ?o}'%(GRAPH,uid)
                        result_set = self.db.query(sq)

                        actor_num = 0
                        actor_name=""
                        actor_id = ""
                        for p,o in result_set:
                            p = "<%s>"%p
                            pname = predictmap['actor_node'][p]
                            if pname == 'actor_number': actor_num = int(o) - 1
                            elif pname == 'actor_name': actor_name = o
                            elif pname == 'actor_id': actor_id = o
                        actor_info[actor_num]['name']=actor_name
                        if actor_id != "": actor_info[actor_num]['id']=actor_id
                    result[u'演员表'] = actor_info
                else:
                    for uid in objects[pname]:
                        print uid,pname
                        name = self.get_entity_label(uid)
                        result[pname].append({'id':uid,'name':name})
            return result
        def get_type(entity_id):

        result =  get_objectinfo(result,objects)
        result2 = {}
        infobox = {}
        for pname in result:
            if pname in predictmap['common']:
                result2[pname] = result[pname]
            else: infobox[pname] = result[pname]
        result2['Infoboxes'] = infobox
        return result2

if __name__ == "__main__":
    configs = ConfigTool.parse_config("./config/db.cfg","MovieKB")
    mkb = MovieKB()
    #print mkb.get_prop_entities("b10050542")
    fw = codecs.open('test.txt','w','utf-8')
    fw.write(json.dumps(mkb.get_entity_info("b10004047"),ensure_ascii=False))
    fw.close()

