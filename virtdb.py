#!/usr/bin/env python
#-*-coding=utf-8-*-

from jpype import *

import os
import sys

import pyodbc
import codecs

from urllib import *

from utils import *

class VirtDB(object):
    """
    """

    def __init__(self, uid, pwd, graph, dsn=None, host=None, port=None):
        self.HOST = host
        self.PORT = port
        self.DSN = dsn 
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



class OdbcVirtDB(VirtDB):
    """
    """

    def __init__(self, uid, pwd, graph, dsn=None, host=None, port=None, driver=None):
        virtDB.__init__(self, uid, pwd, graph, dsn, host, port)

        self.db = None

    def connect(self):
        pass

    def query(self, sq):
        if self.DSN:
            self.db = pyodbc.connect("DSN=%s; UID=%s; PWD=%s;charset=%s"%(self.DSN, self.UID, self.PWD, self.charset) )
        elif self.DRIVER:
            self.db = pyodbc.connect('DRIVER=%s;HOST=%s:%d;UID=%s;PWD=%s;charset=UTF-8'%(DRIVER, HOST, PORT, UID, PWD))
        else:
            raise ValueError("Need DSN or DRIVER&&HOST&&PORT")

        sq = "sparql " + sq
        cursor = self._virtodb.cursor()
        try:
            results = [r[0] for r in cursor.execute(sq).fetchall()]
            if results and len(results) > 0 and type(results[0]) == tuple:
                results = [r[0] for r in results]
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

        self.jvmpath = getDefaultJVMPath()
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
        print (result)
        for r in result:
            r_list.append((r.getK(), r.getV()))
        return r_list

    def close(self):
        shutdownJVM()

if __name__ == "__main__":
    configs = ConfigTool.parse_config("./config/db.cfg","MovieKB")
    configs.pop("driver")
    db = JenaVirtDB(**configs)
    string = "select * where {<http://keg.tsinghua.edu.cn/movie/instance/" + str(11510446) + "> ?p"+" ?o}"
    print (string)
    for r in db.query(string):
        print (r[0]+" "+r[1])
    

