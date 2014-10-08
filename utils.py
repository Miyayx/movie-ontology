#/usr/bin/python2.7
#encoding=utf-8
import codecs
import platform
v= platform.python_version()

if v.startswith('2') :
    from ConfigParser import ConfigParser
elif v.startswith('3') :
    from configparser import ConfigParser

def common_items(a,b):
    """
    Find the common element of the two lists
    Will change the sequence
    """
    return list(set(a) & set(b))

def diff_items(a,b):
    """
    Find the different element between the two lists
    Will change the sequence
    """
    return list(set(a)^ set(b))

class ConfigTool():
    @staticmethod
    def parse_config(fn, section):
        cf = ConfigParser()
        cf.read(fn)
        return dict(cf.items(section))
        
