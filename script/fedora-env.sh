#!/bin/sh
#Virtuoso
yum install unixODBC unixODBC-devel
pip install pyodbc 

#Third-party package
pip install numpy
pip install nltk

pip install jieba
pip install marisa_trie
