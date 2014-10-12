#!/usr/bin/env python
#-*-coding:utf-8-*-

from twisted.web.resource import Resource
from twisted.web import server, resource, http
from twisted.web.static import File

import simplejson

from db import *

DSN = "VOS"

class VirtResource(Resource):

    def render_GET(self, request):
        print "GET"
        return ""

    def render_POST(self, request):
        """
        request args need:
        id_
        type
        prefix
        graph
        uid
        pwd
        dsn
        """
        print "POST"

        request.setHeader("Access-Control-Allow-Origin","*")
        request.setHeader("Content-Type","application/json")

        args = dict((k,v[0]) for k,v in request.args.items())
        print "request args:",args

        #sq = 'select * from <%s> where {<%s/%s/%s> ?p ?o}'%(
        #        args["graph"],
        #        args.pop("prefix").strip("/"),
        #        args.pop("type").strip("/"),
        #        args.pop("id_")
        #        )

        sq = args.pop("sq")
        args.pop("prefix")

        db = OdbcVirtDB(**args)
        results = db.query(sq)

        return simplejson.dumps(results)

if __name__=="__main__":
    root = Resource()
    root.putChild("query", VirtResource())

    from twisted.internet import reactor

    reactor.listenTCP(5678, server.Site(root))
    reactor.run()

