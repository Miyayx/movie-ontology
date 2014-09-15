#!/usr/bin/env/python2.7
#-*-coding:UTF-8-*-

class LittleEntity():

    def __init__(self, _id, uri, type, title, super_topic, abstract, image, related_item ):
        self._id        = _id
        self.uri        = uri
        self.url        = url
        self.type     = type
        self.super_topic = super_topic
        self.title    = title
        self.abstract = abstract
        self.image    = image
        self.related_item    = related_item

    def __str__(self):
        return "title:"+str(self.title)+"#"+"uri:"+str(self.uri)+"image_url:"+str(self.image)




