#encoding=utf-8
'''
Created on 2014-9-10

@author: 张江涛
'''
import codecs
import re
import json

class preProcessing():
    def __init__(self,inf,outf,title,m_id,d_id):
        self.inf = inf
        self.outf = outf
        self.title = title
        self.m_id = m_id
        self.d_id = d_id
        
    def load_txt(self):
        fi = codecs.open(self.inf, 'r', "utf-8")
        fo = codecs.open(self.outf,'w',"utf-8")
        fo.write('Title:' + self.title +':::' + self.m_id + ':::' + self.d_id +'\n')

        for line in fi:
            if "content" in line:
                str = line[14:]
                content = str.split("title")[0][:-3]
#                 print(str)
#                 print(content)
                fo.write("::::" + content + "\n")
        fi.close()
        fo.close()
    def load_json(self):
        fi = codecs.open(self.inf, 'r', "utf-8")
        fo = codecs.open(self.outf,'w',"utf-8")
        fo.write('Title:' + self.title +':::' + self.m_id + ':::' + self.d_id +'\n')
        for line in fi:
            if "{" in line and "content" in line:
                main = line[line.find("{"):]
                try:
                    comment_dict = json.loads(main)
                    fo.write("::::" + comment_dict["content"] +"\n")
                except:
                    print(line)
                    continue
        fi.close()
        fo.close()
        
if __name__ == '__main__':
    process = preProcessing("./data/comment/2/part-r-00000","./data/test/2-part-r-0000","绣春刀","dt10063250","24745500")
    process.load_json()
    
                
                