# -*- coding: utf-8 -*-
import time
import os
import copy
import datetime
import sys
import re
import math
import json
import codecs
import traceback

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

def is_latin(uchar):
		"""判断一个unicode是否是拉丁字母"""
				
		if (uchar >= u'\u00c0' and uchar<=u'\u0190'):
				return True
		else:
				return False
			    
def is_other(uchar):
		"""判断是否非汉字，数字和英文字符"""
		if not (is_chinese(uchar) or is_number(uchar) or is_alphabet(uchar)):
				return True
		else:
				return False


#处理描述性文字,注意只能处理一次，多次处理会出错,处理Image等已经有转义的字符，不能进行转义

#去掉换行，转义\",转义\u
def getEscapeTxt(descriptStr):
	#'"' 相当于 "\"", 所以少了一个\, 最后一行中，是由于json需要使用:,所以进行转义，其实没有必要，因为其他地方没有用到
	#而我一般用,做字符串的分割符
	retstr = descriptStr.replace("\r"," ").replace("\n"," ")
	#第一个二进制是08， 第二个是07 第三个是10，第四个是1A，能不能全部都
	controlstr="\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f"
	for c in controlstr:
		retstr = retstr.replace(c,"")
	retstr = retstr.replace("\\","\\\\").replace('"','\\"')
	#retstr = retstr.replace(":","\:").replace(",","\,")

	return retstr

#读数据, 根据前一行的信息，读取后一行的信息。这是因为读取数据时，由于错误分行导致
def breadline(fp):
	p = fp.readline()
	if p is None: nret = -2
	pos = p.find(':')
	return p, pos


def readOneBlock(pstr,posid,fp):
	data = {}
	preKey = pstr[:posid]
	data[preKey] = pstr.strip()
	while 1:
		p,pos = breadline(fp)
		if pos == -2: break
		elif pos==-1 or pos>20:
			if len(p.strip())>2:
				data[preKey] += p.strip()
			else: break
		else:
			preKey = p[:pos]
			data[preKey] = p.strip()

	return data

#写数据函数,按字段顺序写入
def writeOneBlock(fin, data):
	fields = ['ID','Title','URL','Summary','IsMovie','Categories','Infoboxes','InnerLinks','FirstImage','Images','FullText','ExternalLinks']
	fw = codecs.open(fin,'a',"utf-8")
	for fd in fields:
		if fd in data: fw.write(data[fd].strip()+"\n")
	fw.write("\n")
	fw.close()

#写数据函数,按字段顺序写入
__fields = ['Title','URL','Summary','IsMovie','Categories','Infoboxes','InnerLinks','FirstImage','Images','ExternalLinks','FullText', "doubanURL","subtype" ]
def writeOneBlock2line(fin, data):	#分隔符用!!:
	fw = codecs.open(fin,'a',"utf-8")
	fw.write(data['ID'])
	for fd in __fields:
		if fd in data: fw.write("!!:%s"%data[fd].strip())
	fw.write("\n")
	fw.close()


def readOneline(fp):	#分隔符用!!:
	p = fp.readline()
	strs = p.strip().split('!!:')
	data={}
	if len(strs)<3: return data

	#data['ID'] = strs[0][4:]
	for keystr in strs:
		pos = keystr.find(': ')
		if pos==-1 or pos>20: continue
		propkey = keystr[:pos]
		propvalue=keystr[pos+2:]
		data[propkey] = propvalue
	return data

#需要改进
'''
			if key not in ['Summary','FullText']:
				fw.write(',"%s":"%s"'%(key,data[key])))
			else:
				fw.write(',"%s":"%s"'%(key,getEscapeTxt(data[key])))
'''
def writedata2json(fout,data,infobox):
	fw = codecs.open(fout,'a',"utf-8")
	fw.write('{ "ID":"%s"'%data['ID'])
	for key in __fields:
		if key in data:
			if key == 'Infoboxes': continue
			fw.write(',"%s":"%s"'%(key,getEscapeTxt(data[key])))
	fw.write(',"Infoboxes":{')
	if len(infobox)>0:
		ftuple = list(infobox.items())
		fw.write('"%s":"%s"'%(ftuple[0][0],getEscapeTxt(ftuple[0][1])))
		for t in ftuple[1:]:
			fw.write(',"%s":"%s"'%(t[0],getEscapeTxt(t[1])))

	fw.write("}}\n")
	fw.close()

#属性值处理算法， 修改：去掉链接信息
def getPropName(Propstr):

	propfilter = u" \t0123456789:：、，|,。.；;/\\　\""
	propName = ""
	Propstr = Propstr.replace("\\","/")
	#查找并去掉链接
	while 1:
		pos1 = Propstr.find('[[')
		pos2 = Propstr.find('||')
		pos3 = Propstr.find(']]')
		if pos1>-1 and pos2>pos1 and pos3>pos2:
			Propstr = Propstr[:pos1]+Propstr[pos1+2:pos2]+Propstr[pos3+2:]
			continue
		break
	for i in range(len(Propstr)):
		if Propstr[i] not in propfilter: propName += Propstr[i]

	return propName.lower()

#获取Infobox
def getInfobox(infoboxstr):
	key = infoboxstr.split('::;')
	infobox = {}
	for vk in key:
		v = vk.split('::=')
		if len(v)==2:
			kv = getPropName(v[0])
			infobox[kv] = v[1]
	return infobox

def readHighWeight(w):
    splitc = [u"，","/","\\",u"、",u"；"]
    retstr = w
    for c in splitc:
        retstr = retstr.replace(c,',')
    value = retstr.split(',')
    high   = value[0].strip()
    weight = ""
    if len(value)>1:
        weight = value[1].strip()
    return high,weight

def getlinks(baidulink):
	bArray = baidulink.replace('[',"").replace(']',"").split("||")
	bArray[0]=bArray[0].strip()
	return bArray

#一下这个函数非常重要，需要从长计议，错误引入之源， 其实是mention识别函数
'''
estr1 = u'[[国光帮||/view/405956.htm]]帮忙,[[红楼梦||/view/2571.htm]]中人'
estr2 = u'[[李升燕||/view/1670526.htm]] （[[李成延||/view/1264893.htm]] [[李承延||/view/8367130.htm]]）'
estr3 = u'[[江苏||/view/4141.htm]][[常州||/view/5198.htm]]'
ss = u"我是《[[敢不敢||/view/3003088.htm]]》、《[[不死的青春||/view/6633207.htm]]》"
estr1 = u'[[国光帮||/view/405956.htm]]帮忙,[[红楼梦||/view/2571.htm]]中人'''
#返回两个列表，纠错，并且要保持顺序，顺序不能乱的。
#是不是应当分为 《文字性》 和 《对象型》 的分割函数

#以后改进为的mention识别函数，分隔符不能用,了，因为,为多链接的分割符，多连接分割符改用.
def getPropValue(propvalue):
	dropchar = ['[[',u"！","!",u"“","\\",u"。",'"',u"《",u"》"] #"()（）"很纠结这些符号要不要去掉
	#两种情况，要纠错，能够正确的分隔数据时非常重要的
	splitchar = ["] ","][","/", u"，", u"、", ';',u"；"]

	#处理链接，[[中国||...]]合伙人 link错误  [[]]等
	mstr = ""
	retstr = propvalue.replace('::;',',')
	linkmap = {}
	linkstr = retstr
	linelen = len(retstr)
	oldpos1 = 0
	oldpos2 = 0
	while oldpos2<linelen:
		pos1 = linkstr.find('[[',oldpos2)
		pos2 = linkstr.find(']]',oldpos2)
		#处理link信息
		if pos1==-1 or pos2==-1:
			mstr += linkstr[oldpos2:]
			break
		mstr += linkstr[oldpos2:pos1]
		#print mstr
		#到了最后
		if pos2+2>=linelen:
			links = getlinks(linkstr[pos1:pos2])
			linkmap[links[0]]=links[1]
			mstr+=links[0]
			break
		else:
			#按顺序查找,判断pos2后面的数据第一个字符是非有效字符（分隔符）
			links = getlinks(linkstr[pos1:pos2])
			mstr += links[0]

			#有效链接
			if is_other(linkstr[pos2+2]):
				linkmap[links[0]]=links[1]
				mstr+=','

		#定点游标
		oldpos2 = pos2+2

	#split以及过滤字符
	for c in splitchar:
		mstr = mstr.replace(c,",")
	for c in dropchar:
		mstr = mstr.replace(c,"")

	kv = mstr.split(',')
	vk = kv[0].strip()
	retstr = vk
	if vk in linkmap: retstr+='|'+linkmap[vk]
	for v in kv[1:]:
		vk = v.strip()
		if len(vk)>0:
			retstr += ','+vk
			if vk in linkmap: retstr+='|'+linkmap[vk]
	return retstr

#getPropValue(ss)
#此为文字型属性值，去除链接信息，尽量不要引入错误
def getNameValue(propvalue, mtype):
	dropchar = ['[[', u"！","!",u"“","\\",u"。",'"',u"《",u"》"] #"()（）"很纠结这些符号要不要去掉
	#两种情况，要纠错，能够正确的分隔数据时非常重要的
	splitchar = ["/", u"、", ';',u"；"]

	if mtype!='movie': splitchar.append(u'，')

	#处理链接，[[中国||...]]合伙人 link错误  [[]]等
	mstr = ""
	retstr = propvalue.replace('::;',':::') #名字中也有,的形式出现，分隔符不应该加上，和:, ";"应该替换一下
	linkstr = retstr
	linelen = len(retstr)
	oldpos1 = 0
	oldpos2 = 0
	while oldpos2<linelen:
		pos1 = linkstr.find('[[',oldpos2)
		pos2 = linkstr.find(']]',oldpos2)
		#处理link信息
		if pos1==-1 or pos2==-1:
			mstr += linkstr[oldpos2:]
			break
		mstr += linkstr[oldpos2:pos1]
		#print mstr
		#到了最后
		if pos2+2>=linelen:
			links = getlinks(linkstr[pos1:pos2])
			mstr+=links[0]
			break
		else:
			#按顺序查找,判断pos2后面的数据第一个字符是非有效字符（分隔符）
			links = getlinks(linkstr[pos1:pos2])
			mstr += links[0]

			#有效链接
			if is_other(linkstr[pos2+2]):
				mstr+=':::'

		#定点游标
		oldpos2 = pos2+2

	#split以及过滤字符
	for c in splitchar:
		mstr = mstr.replace(c,":::")
	for c in dropchar:
		mstr = mstr.replace(c,"")

	kv = mstr.split(':::')
	retstr = ""
	for v in kv:
		vk = v.strip()
		if len(vk)==0: continue
		if vk[0] in u"(（": continue
		retstr += vk+'::;'
	if '::;' in retstr:
		retstr = retstr[:-3]
	return retstr

#getPropValue(ss)

# /subview/946364/8871166.htm=>/view/946364.htm 后面去掉
# #sub去掉， http去掉
def getUrl(url):
	rurl = url.replace("http://baike.baidu.com","").split("#")[0]
	if "subview" in rurl:
		pos1 = rurl.find('subview/')+len('subview/')
		pos2 = rurl.find('/',pos1)
		urlid = rurl[pos1:pos2]
		rurl = "/view/%s.htm"%urlid
	return rurl

#从名称列表中获取非重复的mention, 去掉()[]（）内的说明信息
#小写，去link,name也可能包含多个name
def getmentions(names):
	mentions = []
	for name in names:
		namesplit = getPropValue(name).split(',')
		for nt in namesplit:
			m = getmention(nt).lower()
			if len(m)==0:continue
			if m not in mentions: mentions.append(m)
	return mentions

def getmention(name):
	splitchar = u"([（"
	clearchar = u"《》"
	m=name.strip().lower()
	if len(m)==0: return ""
	if "[[" in m:
		m = m.replace("[[","").split("||")[0]
	for c in splitchar:
		if c in m: m = m.split(c)[0].strip()
	for c in clearchar:
		if c in m: m = m.replace("c","")
	return m

#处理title, 从baidu作品的title中获取进一步的信息，比如year,比如season和类别信息
def gettype(title,typearray):
	filmtype = [u"电影"]
	tvtype = [u"连续剧",u'电视']
	for t in filmtype:
		if t in title:  return 1
	for t in tvtype:
		if t in tvtype: return 2
	return 0

#生成season词典文件
def printSeason():
	number_zh = [u"一",u"二",u"三",u"四",u"五",u"六",u"七",u"八",u"九",u"十"]
	seasonkey = [u"部",u"季",u"辑",u"作"]
	ss = u"零"
	print(u"零")
	for j in range(9):
		print(number_zh[j])
		ss += ","+number_zh[j]
	for i in range(5):
		for j in range(10):
			if i==0:
				if j==0:
					print ("%s"%(number_zh[9]))
					ss += ",%s"%(number_zh[9])
				else:
					print ("%s%s"%(number_zh[9],number_zh[j-1]))
					ss += ",%s%s"%(number_zh[9],number_zh[j-1])
			else:
				if j==0:
					print ("%s%s"%(number_zh[i],number_zh[9]))
					ss += ",%s%s"%(number_zh[i],number_zh[9])
				else:
					print ("%s%s%s"%(number_zh[i],number_zh[9],number_zh[j-1]))
					ss += ",%s%s%s"%(number_zh[i],number_zh[9],number_zh[j-1])

	zh_nums = ss.split(',')

	fw = codecs.open("seasonInTitle.dic",'w',"utf-8")
	for i in range(len(zh_nums)):
		for j in range(len(seasonkey)):
			fw.write(u"第%s%s:%d\n"%(zh_nums[i],seasonkey[j],i))
			fw.write(u"第%s%s:%d\n"%(i,seasonkey[j],i))
	fw.close()

def getyear(yearstr):
	number = "0123456789"
	pos = yearstr.find(u'年')
	retyear = yearstr
	if pos !=-1:
		#有关键字年
		if pos == 4: retyear = yearstr[:pos]
		elif pos>4:  retyear = yearstr[pos-4:pos]
	if len(retyear)==4:
		bNumber = True
		for i in range(4):
			if retyear[i] not in number:
				bNumber = False
				break
		if bNumber: return retyear
	return ""

#print getyear(u"1988"), getyear(u"1988年"), getyear(u"战争（1988）")

def readSeasonDic():
	seasontype = {}
	fp = codecs.open("seasonInTitle.dic",'r',"utf-8")
	for p in fp.readlines():
		key = p.strip().split(':')
		seasontype[key[0]] = key[1]
	fp.close()
	return seasontype
#seasontype = readSeasonDic()
def getseasons(title):
	if "第".decode('utf-8') in title:
		for s in seasontype:
			if s in title:
				return seasontype[s]
	return ""
#print getseasons(u"中国好声音（第一季）"),getseasons(u"越狱第三季")


def getAliasString(data):
	namestr = data['Title']
	if 'alias' in data['Infoboxes']:
		namestr+='::;'+data['Infoboxes']['alias']
	mtype = 'p'
	if u'演员表' in data['Infoboxes'] or u'导演' in data['Infoboxes'] : mtype='movie'
	qcbuf = []
	alias = ""
	for a in getNameValue(namestr,mtype).split('::;'):
	    if mtype=='p':
	        a = a.split('(')[0].split(u'（')[0]
	    a = a.strip().lower()
	    if len(a.encode('utf-8'))<3 or a in [u"男",u"女",u"male",u"female"]:continue
	    if a not in qcbuf:
	        qcbuf.append(a)
	        alias += '::;%s'%a
	return alias

def compareSet(set1, set2):
	nret = False
	for elem1 in set1:
		if elem1 in set2:
			nret = True
			break
	return nret
