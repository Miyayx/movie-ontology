Movie-Ontology
====================

EntityLinking part of Movie-Ontology

##Python
  Using python3.X
### pip
  * Windows
  > download [pip](http://www.lfd.uci.edu/~gohlke/pythonlibs/#pip)

keg@Tsinghua

##Database
###MySQL
* Fedora:
    ```
    yum install MySQL-python
    ```

* Ubuntu:
    ```
    apt-get install libmysqlclient-dev python-dev
    pip install MySQL-python
    ```
    
* Windows
    > download [MySQL-python](http://www.lfd.uci.edu/~gohlke/pythonlibs/#mysql-python)

###Virtuoso
* Fedora:
    ```
    yum install unixODBC unixODBC-devel
    pip install pyodbc 
    ```

* Ubuntu:
    ```
    apt-get install unixODBC unixODBC-dev
    pip install pyodbc 
    ```
* Windows 
    > download [pyodbc](http://www.lfd.uci.edu/~gohlke/pythonlibs/#pyodbc)
    > download [Single-tier ODBC Driver for Virtuoso](http://download.openlinksw.com/solwiz/view_solution.php?solutions_id=52104&solution_num=1) need sign up and sign in
    > set odbc driver config [Windows ODBC Driver Configuration](http://docs.openlinksw.com/virtuoso/odbcimplementation.html)


Setting：

##Third-party package
* nltk 

    ```
    pip install numpy
    pip install nltk
    ```
    > Windows:[nltk](http://www.lfd.uci.edu/~gohlke/pythonlibs/#nltk)

> need nltk.download() to download nltk corpas

* marisa-trie
    ```
    pip install marisa
    ```
    > Windows:[marisa-trie](http://www.lfd.uci.edu/~gohlke/pythonlibs/#marisa-trie)

* twisted 
    ```
    pip install twisted
    ```

##Server Start Step

1. start web server

    ```
    python webserver.py  in movie-ontology/
    ```
##Test Demo
        python web_test.py
    
Movie-Ontology
====================

EntityLinking part of Movie-Ontology

##Python
  Using python3.X
### pip
  * Windows
  > download [pip](http://www.lfd.uci.edu/~gohlke/pythonlibs/#pip)

keg@Tsinghua

##Database
###MySQL
* Fedora:
    ```
    yum install MySQL-python
    ```

* Ubuntu:
    ```
    apt-get install libmysqlclient-dev python-dev
    pip install MySQL-python
    ```
    
* Windows
    > download [MySQL-python](http://www.lfd.uci.edu/~gohlke/pythonlibs/#mysql-python)

###Virtuoso
* Fedora:
    ```
    yum install unixODBC unixODBC-devel
    pip install pyodbc 
    ```

* Ubuntu:
    ```
    apt-get install unixODBC unixODBC-dev
    pip install pyodbc 
    ```
* Windows 
    > download [pyodbc](http://www.lfd.uci.edu/~gohlke/pythonlibs/#pyodbc)


Setting：

##Third-party package
* nltk 

    ```
    pip install numpy
    pip install nltk
    ```
    > Windows:[nltk](http://www.lfd.uci.edu/~gohlke/pythonlibs/#nltk)

> need nltk.download() to download nltk corpas

* marisa-trie
    ```
    pip install marisa
    ```
    > Windows:[marisa-trie](http://www.lfd.uci.edu/~gohlke/pythonlibs/#marisa-trie)

* twisted 
    ```
    pip install twisted
    ```

##Server Start Step

1. start web server

    ```
    python webserver.py  in movie-ontology/
    ```
##Test Demo
        python web_test.py
    
