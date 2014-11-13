#coding=utf-8

import sys,datetime,string,re,os,jieba
import config

def test():
    vocabList = []
    lines = open(config.vocabulary_path).readlines()
    for line in lines:
        arrLine = re.split(r'\t',line)
        if len(arrLine)==4:
            vocabList.append(arrLine[0])
    startTime = datetime.datetime.now()
    bagOfWords2VecMN(vocabList, "吃葡萄吐葡萄皮")
    secondTime = datetime.datetime.now()
    bagOfWords2VecMN2(vocabList, "吃葡萄吐葡萄皮")
    print 'time1 is : %s' % (secondTime-startTime)
    print 'time2 is : %s' % (datetime.datetime.now() - secondTime)


def bagOfWords2VecMN(vocabList, inputSet):
    returnVec = {}
    for word in inputSet:
        if word in vocabList:
            index = vocabList.index(word)
            if not returnVec.has_key(index):
                returnVec[index] = 1
            elif returnVec[index]<3:
                returnVec[index] += 1
    return returnVec


def bagOfWords2VecMN2(vocabList, inputSet):
    returnVec = {}
    for word in vocabList:
        if word in inputSet:
            index = vocabList.index(word)
            if not returnVec.has_key(index):
                returnVec[index] = 1
            elif returnVec[index]<3:
                returnVec[index] += 1
    return returnVec
