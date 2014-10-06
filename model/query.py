#!/usr/bin/env python2.7
#encoding=utf-8

class Query():

    def __init__(self, text, index):
        self.text = text
        self.index = index
        self.candidates = []
        self.entities = []

    def __str__(self):
        return "Text: "+self.text.encode("utf-8")+","+"Index: "+str(self.index)+"\nEntities:"+str(self.entities)
