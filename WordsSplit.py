#encoding=utf-8
import time
import os
import copy
import datetime
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import re
import math
import json
import traceback
import codecs
import string
from basecode import *


class SplitByLanguage():
    def __init__(self):
        self.mapTw_zh = self.getUnicodedic("UGB.inc")
        return
    
    def getUnicodedic(self,dicname):
        #获取繁体字典        
        d = "{"
        f = open(dicname)
        for p in f:            
            h = p.strip().split(':')
            if len(h)==2:
                if len(d)>1: d+=','
                d += '"\\u%s":"\\u%s"'%(h[1],h[0])
        f.close()
        d += "}"
        return json.loads(d)
        
    def is_zhtw(self,c):
        return c in self.mapTw_zh
    
    """
    以空格tab等为分词符，然后判断语种，按照语种,将词分为两个部分
    """   
    def splitNames(self,name):
        #print name
        cname = self.clearPairs(name) #? lower可以么，lower()应该不是这里的工作
        names = cname.split() 
        
        splitpos = 0  #分割点
        
        i = 0
        while i < len(names):
            
            n = names[i].strip()
            i += 1
            if len(n)<1: continue
     
            #去除最开始的数字标点
            s1 = self.getNameType(n)
            while s1==4 and i<len(names)-1:                
                n = names[i].strip()
                i += 1
                if len(n)>0: s1 = self.getNameType(n)                
            
            #part 1
            s2 = -1                        
            while i<len(names):
                
                n = names[i].strip()
                i += 1
                
                if len(n)>0:
                    
                    t = self.getNameType(n)
                    if t == 4: continue
                    
                    if t != s1:
                        s2 = s1
                        s1 = t
                        splitpos = i-1
                        break
            '''
            #part 1 exit condition
            if s2==-1 or s2==1: break  
               
            #part 2            
            while i<len(names):
                
                n = names[i].strip()
                i +=1
                
                if len(n) > 0:
                    
                    t = self.getNameType(n)
                    if t == 4: continue
                    
                    if t != s1:
                        s1 = t
                        break
            
            #if i != len(names): splitpos=0   #后面是符合型数据
            
            #if (s1==2 and s2==0) or (s1==0 and s2==2): splitpos=0
            '''
            break

        s = set()
        if splitpos>0 and splitpos<len(names) and s2 != -1 and s1 != s2:
            
            name1 = names[0]
            for i in range(1,splitpos): name1 += " " + names[i]
            
            name2 = names[splitpos]
            for i in range(splitpos+1,len(names)): name2 += " " + names[i]

            s.add(name1)
            s1 = self.splitNames(name2)
            s = s.union(s1)
        else:
            s.add(cname)
        return s

    
    def clearPairs(self,name):
        """去附加信息 ) ） 不考虑嵌套"""  

        def clearPair(name, c1, c2):
            sname = name
            p1 = sname.find(c1)
            p2 = sname.find(c2)
            if p1>=0 and p2==-1: return sname[:p1]
            elif p1>=0 and p2>p1:
                #print sname[p2+1:],clearPair(sname[p2+1:],c1,c2)
                sname = sname[:p1]+ clearPair(sname[p2+1:],c1,c2)            
            return sname

        sname = name

        #只有一个括号的去掉, 要是有两个括号呢
        pairs = {u'（':u"）",'(':")",'[':']','【':'】'}
        for c in pairs:            
            sname = clearPair(sname, c, pairs[c])
        return sname

    
    def getNameType(self,name):
        '''
        判断单词语种 1 中文 2 英文 3 其他语种 4 全部是标点或者数字 0 混合语种
        删除 数字+标点
        #中文+英文=中文，
        中文+其他 & 中文+繁体 等于其他语种，比如日文，韩文
        其他语种：俄文，日韩，繁体
        #纯英文+latin法文德文=英文。
        '''
        delEStr = string.punctuation + ' ' + string.digits  #ASCII 标点符号，空格和数字   
        delCStr = u'《》（）&%￥#@！{}【】：，。、·“”‘’？‧〈〉～'
        translate_table = dict((ord(char), None) for char in delEStr)
        s = name.translate(translate_table)
        translate_table = dict((ord(char), None) for char in delCStr)
        s = s.translate(translate_table)
        
        if len(s)==0: return 4 
        
        bChinese = False 
        bAlpha   = True  
        bOther   = False
        for c in s:            
            if is_chinese(c) and not self.is_zhtw(c):  
                    bAlpha = False
                    if not bOther:  bChinese = True
            elif is_alphabet(c) or is_latin(c):   
                    #bChinese = False
                    bOther = False
            else:
                    bChinese = False
                    bAlpha = False
                    bOther = True
            if not (bChinese or bAlpha or bOther):
                break
        if bChinese: return 1
        elif bAlpha: return 2
        elif bOther: return 3
        return 0  #0是混合
      
def getNamesFromMention():
    sbl = SplitByLanguage()
    """
    1 小写/去重/简单分词
    """
    f = codecs.open("./data/movie.mentions","r","utf-8")
    names_dic = {}
    complex_names = {}
    for p in f:
        name = p.split(':<')[0]
        if ' ' in name:
            if name.lower() not in complex_names:
                 complex_names[name] = sbl.splitNames(name)
        #else:
        #    if name not in names_dic: names_dic[name] = 1
    f.close()
    print ("%d : %d"%(len(names_dic),len(complex_names)))
    icount = 0
    fw = codecs.open("complex","w","utf-8")
    for key in complex_names:
        icount += 1
        fw.write("%s"%(key))
        for n in complex_names[key]:
            fw.write('::;%s'%n)
        fw.write('\n')
    fw.close()
    print(icount)

if __name__== '__main__':
#     getNamesFromMention() 
    s = u"around the world in 80 days 八十天环游地球 "
#     s = u"andrás bálint"
#     s = u"这儿一脚，那儿一脚 kopytem sem, kopytem tam 这儿一脚，那儿一脚"
    #s = u"日在校园 スクールデイズ"
    #s = u"四五口径女郎 ms. 45"
    #s = u"josé suárez sánchez"
    #s = u"sakura～听到事件的女人～ sakura～事件を聞く女～"
    #s = u"阿德里安·劳林斯 adrian rawlins"
    #s = u"乞丐歌剧 zebrácká opera"      # 1 0 2
    #s = u"81 diver ハチワンダイバー"
    #s = u"中国电视史 中國電視史"
    #s = u"福星小子3：记得我的爱 urusei yatsura 3: rimenbâ mai rabu"
    #s = u"东京之女 (東)[京]（の）女"
    #s = u"逢坂 良太（おおさか りょうた"
    sbl = SplitByLanguage()
    print(sbl.splitNames(s))
    #print sbl.clearPairs(s)
