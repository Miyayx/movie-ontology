#!/usr/bin/env python2.7
#-*-coding:UTF-8-*-

from twisted.web.resource import Resource
from twisted.web import server, resource, http
from twisted.web.static import File

import simplejson

from db import *

PREFIX = "http://keg.cs.tsinghua.edu.cn/instance/"

class LinkingResource(Resource):

    def render_GET(self, request):
        request.setHeader("Access-Control-Allow-Origin","*")
        request.setHeader("Content-Type","application/json")
        
        return self.render_POST(request)

    def render_POST(self, request):
        request.setHeader("Access-Control-Allow-Origin","*")
        request.setHeader("Content-Type","application/json")

        # 调用virtdb.py 或 db.py
        # Return json格式的数据封装
        return 


class PageResource(Resource):
     
    def render_GET(self,request):
        request.setHeader("Access-Control-Allow-Origin","*")
        request.setHeader("Content-Type","application/json")
        return " Hello World!"

if __name__=="__main__":
    root = Resource()
    root.putChild("show", File("./graph-showpage"))
    root.putChild("linking", LinkingResource())

    from twisted.internet import reactor

    reactor.listenTCP(5656, server.Site(root))
    reactor.run()


