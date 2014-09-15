#/usr/bin/python2.7
#encoding=utf-8
import codecs
from ConfigParser import ConfigParser

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
        
