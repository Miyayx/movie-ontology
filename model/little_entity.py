#!/usr/bin/env/python2.7
#-*-coding:UTF-8-*-

class LittleEntity():

    def __init__(self, id_, uri, title, alias = None, abstract=None, image=None):
        self.id_        = id_
        self.uri        = uri
        self.title    = title
        self.alias    = alias
        self.abstract = abstract
        self.image    = image

    def __str__(self):
        return "title:"+str(self.title)+"\n"+"uri:"+str(self.uri)+"\nimage:"+str(self.image)+"\nabstract:"+str(self.abstract)




