#coding=utf-8

from numpy import *
import sys,datetime,string,re,os,jieba
import config

reload(sys)
sys.setdefaultencoding('utf8')


def sortVocab():
    lines = open(config.vocabulary_path+".bak").readlines()
    vocabs = [];
    for line in lines:
        arrLine = re.split(r'\t',line)
        if len(arrLine)==4:
            vocabs.append({
                "word" : arrLine[0],
                "p0V" : float(arrLine[1]),
                "p1V" : float(arrLine[2])
                })
    vocabs.sort(lambda x,y: cmp(y["p0V"]+y["p1V"], x["p0V"]+x["p1V"]))

    pSpam = float(re.split(r'\t',lines[0])[3])

    f = open(config.vocabulary_path,'w')
    for i in range(len(vocabs)):
        f.writelines("%s\t%s\t%s\t%s\r\n"%(vocabs[i]['word'],vocabs[i]['p0V'],vocabs[i]['p1V'],pSpam))