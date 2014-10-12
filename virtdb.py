#!/usr/bin/env python
#-*-coding=utf-8-*-
import os
import sys
import re

import pyodbc
import codecs

if not re.match('linux',sys.platform):
    from jpype import *

import urllib 
if sys.version[0] == '3':
    import urllib.request as urllib2
    from urllib.parse import urlencode
    
else: 
    import urllib2
    from urllib import urlencode 

import json

from utils import *

class VirtDB(object):
    """
    """

    def __init__(self, uid, pwd, graph, dsn=None, driver=None, host=None, port=None):
        self.HOST = host
        self.PORT = port
        self.DSN = dsn 
        self.DRIVER = driver
        self.UID = uid 
        self.PWD = pwd 
        self.GRAPH = graph
        self.charset="UTF-8"

    def connect(self):
        raise NotImplementedError("Subclasses should implement this!")

    def query(self, sq):
        raise NotImplementedError("Subclasses should implement this!")

    def close(self):
        raise NotImplementedError("Subclasses should implement this!")

class HttpDB(VirtDB):
    def __init__(self, url, uid, pwd, graph, host, port, prefix, dsn, driver):
        VirtDB.__init__(self, uid, pwd, graph, dsn, driver, host, port)

        self.url = url
        self.prefix = prefix

    def connect(self):
        pass

    #def query(self, t, id_):
    def query(self, sq):
        """
        request args need:
        id_
        type
        prefix
        graph
        host
        port
        uid
        pwd
        """

        param = {
                #"id_":id_,
                #"type":t,
                "sq":sq,
                "prefix":self.prefix,
                "graph":self.GRAPH,
                "uid":self.UID,
                "pwd":self.PWD,
                "host":self.HOST,
                "port":self.PORT,
                "dsn":self.DSN,
                "driver":self.DRIVER
                }

        f = urllib2.urlopen(urllib2.Request(self.url, urlencode(param).encode('utf-8')))
        resp = f.read()
        return json.loads(resp.decode('utf-8'))

    def close(self):
        pass


class OdbcVirtDB(VirtDB):
    """
    """

    def __init__(self, uid, pwd, graph, dsn=None, host=None, port=None, driver=None):
        VirtDB.__init__(self, uid, pwd, graph, dsn, driver, host, port)

        self.db = None

    def connect(self):
        pass

    def query(self, sq):
        try:
            if self.DSN:
                self.db = pyodbc.connect("DSN=%s;UID=%s;PWD=%s;charset=%s"%(self.DSN, self.UID, self.PWD, self.charset) )
        except Exception as e:
            print (e)
            if self.driver:
                self.db = pyodbc.connect('DRIVER={%s};HOST=%s:%s;UID=%s;PWD=%s;charset=UTF-8'%(self.DRIVER, self.HOST, str(self.PORT), self.UID, self.PWD))
            else:
                raise ValueError("Need DSN or DRIVER&&HOST&&PORT")

        sq = "sparql " + sq
        cursor = self.db.cursor()
        print ("Query:%s"%sq)
        try:
            results = [(r[0][0], r[1][0]) for r in cursor.execute(sq).fetchall()]
            #if results and len(results) > 0 and type(results[0]) == tuple:
            #    results = [r[0] for r in results]
        except TypeError:
            return []
        finally:
            cursor.close()
            self.db.close()
        return results

    def close(self):
        pass


class JenaVirtDB(VirtDB):
    """
    """

    def __init__(self, uid, pwd, graph, host=None, port=None):
        if not host:
            raise ValueError("Need Value:HOST")
        if not port:
            raise ValueError("Need Value:PORT")
        VirtDB.__init__(self, uid, pwd, graph, host=host, port=port)

        #self.jvmpath = getDefaultJVMPath()
        #startJVM(self.jvmpath, "-ea", "-Djava.ext.dirs={0}".format(os.path.abspath('.')+"/java/"))
        startJVM("C:/Program Files/Java/jre7/bin/server/jvm.dll","-ea","-Djava.ext.dirs={0}".format(os.path.abspath('.')+"/java/"))
        print ("JVM Start")
        VtsDB = JClass('movie.MovieVirt')
        self.db = VtsDB(host, port, uid, pwd, graph)

    def connect(self):
        pass

    def query(self, sq):
        r_list = []
        result = self.db.query(sq)
        for r in result:
            r_list.append((r.getK(), r.getV()))
        return r_list

    def close(self):
        shutdownJVM()

if __name__ == "__main__":
    configs = ConfigTool.parse_config("./config/db.cfg","MovieKB")
    string = "select * where {<http://keg.tsinghua.edu.cn/movie/instance/" + str('b10050542') + "> ?p"+" ?o}"

    #db = JenaVirtDB(**configs)

    configs["url"] = "http://10.1.1.23:5678/query"
    configs["prefix"] = 'http://keg.tsinghua.edu.cn/movie/'

    db = HttpDB(**configs)
    for r in db.query(string):
        print (r[0]+" "+r[1])
    
    #for r in db.query("instance","b10050542"):
    #    print (r[0]+" "+r[1])
        

    

