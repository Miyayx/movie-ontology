#!/usr/bin/env python
#-*-coding=utf-8-*-

import MySQLdb
import pyodbc
import codecs

from urllib import *

from utils import *
from symbol import except_clause

PREFIX = 'http://keg.tsinghua.edu.cn/movie/'

class MovieKB():
    """
    Properties
    --------------------------
    """
    
    configs = ConfigTool.parse_config("./config/db.cfg","MovieKB")
#     print ("configs:"+configs)
    HOST = configs["host"]
    PORT = int(configs["port"])
    UID  = configs["user"]
    PWD  = configs["password"]
    DRIVER = configs["driver"]
    _virtodb = pyodbc.connect('DRIVER=%s;HOST=%s:%d;UID=%s;PWD=%s;charset=UTF-8'%(DRIVER, HOST, PORT, UID, PWD))
    _virtodb = pyodbc.connect("DSN=VOS;UID=dba; PWD=dba;charset=UTF-8"  )
    def __new__(cls, *args, **kwargs):
        if not cls._virtodb:
            cls._virtodb = super(MovieKB, cls).__new__(cls, *args, **kwargs)
        return cls._virtodb

    def __init__(self):
        pass

    def create_conn(self):
        if MovieKB._virtodb:
            MovieKB._virtodb.close()

        print ("Create new connection")
        MovieKB._virtodb = pyodbc.connect("DSN=%s;UID=dba;PWD=dba" %("VOS") )

#         MovieKB._virtodb = pyodbc.connect('DRIVER=%s;HOST=%s:%d;UID=%s;PWD=%s'%(MovieKB.DRIVER, MovieKB.HOST, MovieKB.PORT, MovieKB.UID, MovieKB.PWD))
        #MovieKB._virtodb = pyodbc.connect('DRIVER={VOS};HOST=%s:%d;UID=%s;PWD=%s'%(MovieKB.HOST, MovieKB.PORT, MovieKB.UID, MovieKB.PWD))

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
        self.create_conn()
        sq = 'sparql select * from <keg-movie> where {<%sinstance/%s> ?p ?o}'%(PREFIX,entity_id)
        cursor = self._virtodb.cursor()
        result = {}
        for r in cursor.execute(sq).fetchall():
            result[r[0][0]] = result.get(r[0][0],[]) + [r[1][0]]
        return result

    def parse_properties(self, p2o):

        result = {}

        for p,o in p2o.items():
            key = p.split("/",5)[-1]
            result[key] = o

        return result

    def get_abstract(self, entity_id):
        sq = 'sparql select * from <keg-movie> where {<%sinstance/%s> <%scommon/summary> ?o }'%(PREFIX, entity_id, PREFIX)

        print (sq)

        return self.fetch_one_result(sq)

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

if __name__ == "__main__":
    configs = ConfigTool.parse_config("./config/db.cfg","MovieKB")
#     print ("configs:"+configs)
    HOST = configs["host"]
    PORT = int(configs["port"])
    UID  = configs["user"]
    PWD  = configs["password"]
    DRIVER = configs["driver"]
#     mkb = MovieKB()
#     mkb.get_abstract(11001038)
    #str_conn = "DSN=VOS;UID=dba; PWD=dba;charset = utf-8"
    str_conn = 'DRIVER=%s;HOST=%s:%d;UID=%s;PWD=%s'%(DRIVER, HOST, PORT, UID, PWD)
    #str_conn = "DSN=VOS;UID=dba; PWD=dba;charset = utf-8"

#     mkb = MovieKB()
#     mkb.get_abstract(11001038)
    virto=pyodbc.connect(str_conn,unicode_results=True)
    cursor = virto.cursor()
    entity_id = 11500032
    sq = 'sparql select * from <keg-movie> where {<%sinstance/%s> <%scommon/summary> ?o }'%(PREFIX, entity_id, PREFIX)
    results = cursor.execute(sq)
    try:
        result = results.fetchone()[0]
        print(codecs.decode(result,'utf8'))
        if type(result) == tuple:
            result = result[0]
            print(result)
    except TypeError as e:
        print(e)
    finally:
        cursor.close()

