#!/usr/bin/env python
#-*-coding=utf-8-*-

import pyodbc
import codecs
from urllib import *

from utils import *
from symbol import except_clause
from virtdb import *

PREFIX = 'http://keg.tsinghua.edu.cn/movie/'

class MovieKB():
    """
    Properties
    --------------------------
    """
    
    def __init__(self):
        configs = ConfigTool.parse_config("./config/db.cfg","MovieKB")
        import sys
        if sys.platform == 'linux':
            configs.pop("driver")
            self.db = JenaVirtDB(**configs)
            #self.db = OdbcVirtDB(**configs)
        else:
            configs.pop("driver")
            self.db = JenaVirtDB(**configs)

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
        sq = 'select * from <keg-movie> where {<%sinstance/%s> ?p ?o}'%(PREFIX,entity_id)
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

    def get_abstract(self, entity_id):
        #sq = 'select * from <keg-movie> where {<%sinstance/%s> <%scommon/summary> ?o }'%(PREFIX, entity_id, PREFIX)
        sq = 'select * from <keg-movie> where {<%sinstance/%s> ?p ?o}'%(PREFIX,entity_id)
        result_set = self.db.query(sq)
        for p, o in result_set:
            if p.endswith('common/summary'):
                return o

        #return self.fetch_one_result(sq)

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
    mkb = MovieKB()
    print (mkb.get_abstract(11001038))
    print (mkb.get_instance_properties(11001038))

