#!/usr/bin/python2.7
#encoding=utf-8

"""
Created on 2014-9-10
author: Jiangtao Zhang
"""

import codecs
import re
import marisa_trie

def trie_build(m2e) :
    mentions = m2e.keys()
    trie = marisa_trie.Trie(mentions)
    return trie
   
def m2e_build(fin) :
    fi=codecs.open(fin,'r',"utf-8")
    m2e = dict();
    for line in fi:
        pair = re.split(':',line.strip(),1)
        if len(pair)<2 :
            continue
        mention = pair[0]
        entity = pair[1]
        if mention in m2e.keys() :
            enList = m2e[mention]
            if entity not in enList :
                enList.append(entity)
        else :
            m2e[mention] = [entity]
    return m2e
    fi.close()
    
def save_m2e(m2e,fout):
    fo = codecs.open(fout,'w',"utf-8")
    for mention in m2e :
        fo.write(mention + ':::')
        enList = m2e[mention]
        for entity in enList :
            fo.write(entity + '::;')
        fo.write('\n')
    fo.close()
    
if __name__ == '__main__':
    #m2e = m2e_build('./data/movie.mentions')
    #save_m2e(m2e, './data/mention.entity')
    #trie = trie_build(m2e)
    #trie.save('./data/m2e.trie')
    
    trie = marisa_trie.Trie()
    trie.load('./data/m2e.trie')
    result = trie.keys(u'有幸')
    print(result)
