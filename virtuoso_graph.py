#!/usr/bin/env python2.7
#-*-coding:utf-8-*-

from jpype import *

import os
import sys

class VirtuosoGraph(object):
    def __init__(self):
        self.jvmpath = getDefaultJVMPath()
        startJVM(self.jvmpath, "-ea", "-Djava.ext.dirs="+os.path.abspath('.')+"/java/")
        print "JVM Start"
        VtsDB = JClass('movie.MovieVirt')
        self.db = VtsDB()

    def query(self, q):
        print ("query %s")%q
        return self.db.query(q)

    def shutdown(self):
        shutdownJVM()

if __name__ == "__main__":
    db = VirtuosoGraph()
    string = "select * where {<http://keg.tsinghua.edu.cn/movie/instance/" + str(11500030) + "> ?p"+" ?o}"
    print (db.query(string))

