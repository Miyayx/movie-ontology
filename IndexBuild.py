#encoding=utf-8
'''
Created on 2014-9-10

@author: 张江涛
'''
import codecs
import re
import marisa_trie
from basecode import *
from WordsSplit import SplitByLanguage

def is_blank(uchar):
        """判断一个unicode是否是空格"""
        if uchar == ' ' or uchar == '\t':
                return True
        else:
                return False
            
def is_chinese(uchar):
        """判断一个unicode是否是汉字"""
        if uchar >= u'\u4e00' and uchar<=u'\u9fa5':
                return True
        else:
                return False

def is_number(uchar):
        """判断一个unicode是否是数字"""
        if uchar >= u'\u0030' and uchar<=u'\u0039':
                return True
        else:
                return False

def is_alphabet(uchar):
        """判断一个unicode是否是英文字母"""
        if (uchar >= u'\u0041' and uchar<=u'\u005a') or (uchar >= u'\u0061' and uchar<=u'\u007a'):
                return True
        else:
                return False

def is_other(uchar):
        """判断是否非汉字，数字和英文字符"""
        if not (is_chinese(uchar) or is_number(uchar) or is_alphabet(uchar)):
                return True
        else:
                return False
            
def is_parentheses(uchar):
        """判断是否括号"""
        if uchar in "{（）【《》】[(])}":
                return True
        else:
                return False
            
def extract_cn_pre (str):
    for i in range(0,len(str)):
        if is_alphabet(str[i]) :
            break
    flag = True
    if i != 0 and i < len(str)-1:
        for c in str[i+1:]:
            if  is_chinese(c):
                flag = False
                break
    else :
        flag = False
    if flag :
        for offset in range(1,i+1):
            if is_other(str[i-offset]):
                offset +=1
            else:
                break
#         print(str)
        return str[:i-offset+1]
    else :
        return ""

def split_en_cn (str):
    for i in range(0,len(str)):
        if is_alphabet(str[i]) :
            break
    flag = True
    if i != 0 and i < len(str)-1:
        for c in str[i+1:]:
            if  is_chinese(c):
                flag = False
                break
    else :
        flag = False
    if flag :
        for offset in range(1,i+1):
            if is_other(str[i-offset]):
                offset +=1
            else:
                break
#         print(str)
        return [str[:i-offset+1],str[i:]]
    else :
        return []
    
def extract_parentheses (str):
    for i in range(0,len(str)):
        if is_parentheses(str[i]) :
            break
    if i < len(str)-1 :
        return str[:i].strip()
    else :
        return ""
    
def trunc_parentheses (str):
    par_exists = False
    for i in range(0,len(str)):
        if is_parentheses(str[i]) :
            par_exists = True
            break
    if par_exists :
        return str[:i].strip()
    else :
        return str
    
    
def trie_build(m2e) :
    mentions = m2e.keys()
    trie = marisa_trie.Trie(mentions)
    return trie
   
def m2e_build(fin) :
    fi=codecs.open(fin,'r',"utf-8")
#     print('open begin')
    m2e = dict();
    for line in fi:
#         print(line)
        pair = re.split(':',line.strip(),1)
        if len(pair)<2 :
            continue
        mention = pair[0]
        if len(mention) < 2:
            continue
        entity = pair[1]
        mention = mention.lower()
        
        if len(mention) < 2 or len(trunc_parentheses(mention)) < 2:
            continue
        
#         m2e[mention] = m2e.get(person_name, []) + [entity]
        m2e[mention] = list(set(m2e.get(mention, []) +[entity]))
        m2e[trunc_parentheses(mention)] = list(set(m2e.get(trunc_parentheses(mention), []) +[entity]))
        c_e = split_en_cn(mention)
        if c_e:
            if len(trunc_parentheses(c_e[0])) < 2 or len(trunc_parentheses(c_e[1])) < 2:
                continue
            m2e[trunc_parentheses(c_e[0])] = list(set(m2e.get(trunc_parentheses(c_e[0]), []) +[entity]))
            m2e[trunc_parentheses(c_e[1])] = list(set(m2e.get(trunc_parentheses(c_e[1]), []) +[entity]))
 
        person_name = mention.replace("·","").replace("-","")
        if person_name != mention:
            if len(person_name) < 2 or len(trunc_parentheses(person_name)) < 2:
                continue
            m2e[person_name] = list(set(m2e.get(person_name, []) +[entity]))
            m2e[trunc_parentheses(person_name)] = list(set(m2e.get(trunc_parentheses(person_name), []) +[entity]))
            c_e = split_en_cn(person_name)
            if c_e:
                if len(trunc_parentheses(c_e[0])) < 2 or len(trunc_parentheses(c_e[1])) < 2:
                    continue
                m2e[trunc_parentheses(c_e[0])] = list(set(m2e.get(trunc_parentheses(c_e[0]), []) +[entity]))
                m2e[trunc_parentheses(c_e[1])] = list(set(m2e.get(trunc_parentheses(c_e[1]), []) +[entity]))   
        
#         m2e[mention] = m2e.get(mention, set()) +(entity)
#         m2e[trunc_parentheses(mention)] = m2e.get(trunc_parentheses(mention), set()) +(entity)
#         c_e = split_en_cn(mention)
#         if c_e:
#             m2e[trunc_parentheses(c_e[0])] = m2e.get(trunc_parentheses(c_e[0]), set()) +(entity)
#             m2e[trunc_parentheses(c_e[1])] = m2e.get(trunc_parentheses(c_e[1]), set()) +(entity)
# 
#         person_name = mention.replace("·","")
#         if person_name != mention:
#             m2e[person_name] = m2e.get(person_name, set()) +(entity)
#             m2e[trunc_parentheses(person_name)] = m2e.get(trunc_parentheses(person_name), set()) +(entity)
#             c_e = split_en_cn(person_name)
#             if c_e:
#                 m2e[trunc_parentheses(c_e[0])] = m2e.get(trunc_parentheses(c_e[0]), set()) +(entity)
#                 m2e[trunc_parentheses(c_e[1])] = m2e.get(trunc_parentheses(c_e[1]), set()) +(entity)  
        
                
#         v_m1= extract_cn_pre(mention)
#         if len(v_m1):
#             m2e[v_m1] = list(set(m2e.get(v_m1, []) +[entity]))
#             
#         v_m2 = extract_parentheses(mention)
#         if len(v_m2):
#             m2e[v_m2] = list(set(m2e.get(v_m2, []) +[entity]))
#             
#         v_p1= extract_cn_pre(person_name)
#         if len(v_p1):
#             m2e[v_p1] = list(set(m2e.get(v_p1, []) +[entity]))
#             
#         v_p2 = extract_parentheses(person_name)
#         if len(v_p2) :
#             m2e[v_p2] = list(set(m2e.get(v_p2, []) +[entity]))
        

                
#         if mention in m2e.keys() :
#             enList = m2e[mention]
#             if entity not in enList :
#                 enList.append(entity)
#         else :
#             m2e[mention] = [entity]
    
    return m2e
    fi.close()
    
def m2e_build_www(fin) :
    fi=codecs.open(fin,'r',"utf-8")
#     print('open begin')
    m2e = dict();
    for line in fi:
#         print(line)
        pair = re.split(':',line.strip(),1)
        if len(pair)<2 :
            continue
        mention = pair[0]
        if len(mention) < 2:
            continue
        entity = pair[1]
        mention = mention.lower()
        sbl = SplitByLanguage()
        split = sbl.splitNames(mention)
        for name in split:
            if len(name) < 2:
                continue
#             print(name +": " + entity)
            m2e[name] = list(set(m2e.get(name, []) +[entity]))
            if "·" in name :
                m2e[name.replace("·","")] = list(set(m2e.get(name.replace("·",""), []) +[entity]))
            
        
        
    
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
    m2e = m2e_build_www('./data/movie.mentions_new.mentions')
    print('m2e have been created!')
    save_m2e(m2e, './data/mention.entity_www')
    print('m2e have finished!')
    trie = trie_build(m2e)
    trie.save('./data/m2e.trie')
#     
    trie = marisa_trie.Trie()
    trie.load('./data/m2e.trie')
    result = trie.keys(u'克里夫梅利森')
    print(result)

#     str = u"爱德华诺顿(adh) Edward Norton"
#     str2 = "sjgiklgj"
#     set1 = (str) + (str2)
#     print(set1[0])
#     print(trunc_parentheses(str))
# #     print(extract_cn_pre(str))
#     print(trunc_parentheses(split_en_cn(str)[0]) +" " + trunc_parentheses(split_en_cn(str)[1]))