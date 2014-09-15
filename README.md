Movie-Ontology
====================

EntityLinking part of Movie-Ontology

keg@Tsinghua

##Database
###MySQL
* Fedora:

        yum install MySQL-python

* Ubuntu:

        apt-get install libmysqlclient-dev python-dev
        pip install MySQL-python

###Virtuoso
* Fedora:

        yum install unixODBC unixODBC-devel
        pip install pyodbc 
        pip install rdflib

* Ubuntu:

        apt-get install unixODBC unixODBC-dev
        pip install pyodbc 
        pip install rdflib

Setting：

##Third-party package
* nltk 

        pip install numpy
        pip install nltk

> need nltk.download() to download nltk corpas

* twisted 

        pip install twisted

##Server Start Step

1. start web server

           python webserver.py  in movie-ontology/

##Test Demo
    python web_test.py
