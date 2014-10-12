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

* Linux 
    Add db DRIVER in /etc/odbcinst.ini -> DRIVER
    ```
    [VirtuosoODBC]
    Description     = Virtuoso
    Driver          = /usr/lib64/virtodbc_r.so(your virtuoso driver path)
    Driver64        = /usr/lib64/virtodbc_r.so
    ```
    Add db DSN in /etc/odbc.ini -> DSN
    ```
    [Movie]
    Drvier         = VirtuosoODBC
    Drvier64       = VirtuosoODBC
    Address        = XXX.XXX.XXX.XXX:1111

    Servername and Port seem no use
    ```

    ```
    pyodbc.connect("DSN=%s;UID=%s;PWD=%s;charset=%s"%(self.DSN, self.UID, self.PWD, self.charset) )
    or
    pyodbc.connect('DRIVER={%s};HOST=%s:%s;UID=%s;PWD=%s;charset=UTF-8'%(self.driver, self.HOST, str(self.PORT), self.UID, self.PWD))
    ```


Setting：

##Third-party package
* JPype
        [JPype](https://pypi.python.org/pypi/JPype1-py3)
        [JPype-Windows-python3.4](https://pypi.python.org/packages/3.4/J/JPype1-py3/JPype1-py3-0.5.5.2.win-amd64-py3.4.exe#md5=b59007749ccc968fd6a944fa8610df48)

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
    
