#!/usr/bin/env python2.7
#-*-coding:UTF-8-*-

from twisted.web.resource import Resource
from twisted.web import server, resource, http
from twisted.web.static import File

import json

from db import *

PREFIX = "http://keg.cs.tsinghua.edu.cn/instance/"

class LinkingResource(Resource):

    def render_GET(self, request):
        request.setHeader("Access-Control-Allow-Origin","*")
        request.setHeader("Content-Type","application/json")

        return self.render_POST(request)

    def render_POST2(self, request):
        request.setHeader("Access-Control-Allow-Origin","*")
        request.setHeader("Content-Type","application/json")

        name = dict((k,v[0]) for k, v in request.args.items())['query']
        mkb = MovieKB()
        '''
        uris = mkb.getUriByName(name)
        if len(uris) == 0:
            return json.dumps({})
        u = uris[0].split("/")[-1]
        #p2o = mkb.get_instance_properties(u)
        #return str(json.dumps(mkb.parse_properties(p2o)))

        return str(json.dumps(mkb.get_entity_info(u)))
        '''
        #print name
        #print json.dumps(mkb.searchQuery(name))
        return str(json.dumps(mkb.searchQuery(name)))

    def render_POST(self, request):
        request.setHeader("Access-Control-Allow-Origin","*")
        request.setHeader("Content-Type","application/json")
        param = dict((k,v[0]) for k, v in request.args.items())
        mkb = MovieKB()
        if 'query' in param:
            name = param['query']
            return str(json.dumps(mkb.searchQuery(name)))
        elif 'uri' in param:
			name = param['uri']
			result = mkb.get_entity_info(name)
			result['gtype'] = "instance"
			return str(json.dumps(result))

class PageResource(Resource):

    def render_GET(self,request):
        request.setHeader("Access-Control-Allow-Origin","*")
        request.setHeader("Content-Type","application/json")
        return " Hello World!"

if __name__=="__main__":
    root = Resource()
    root.putChild("show", File("./graph-showpage"))
    root.putChild("query", LinkingResource())

    from twisted.internet import reactor

    reactor.listenTCP(5666, server.Site(root))
    reactor.run()


