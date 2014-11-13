#coding=utf-8

from numpy import *
import sys,datetime,string,re,os,jieba,hashlib
import config

reload(sys)
sys.setdefaultencoding('utf8')

def createVocabList(dataSet):
    # vocabSet = set([])  #create empty set
    # for document in dataSet:
    #     vocabSet = vocabSet | set(document) #union of the two sets
    # return list(vocabSet)
    vocabDict = {}
    i = 0
    for document in dataSet:
        for word in document:
            key = hashlib.md5(word).hexdigest()
            if not vocabDict.has_key(key):
                vocabDict[key] = {"n":i,"word":word}
                i += 1

    return vocabDict


# 使用bagOfWords2VecMN代替
# def setOfWords2Vec(vocabList, inputSet):
#     returnVec = [0]*len(vocabList)
#     for word in vocabList:
#         if word in inputSet:
#             returnVec[vocabList.index(word)] = 1
#         else: print "the word: %s is not in my Vocabulary!" % word
#     return returnVec

def trainNB0(trainMatrix,trainCategory,numWords):
    numTrainDocs = len(trainMatrix) #记录条数
    pAbusive = sum(trainCategory)/float(numTrainDocs)
    p0Num = ones(numWords); p1Num = ones(numWords)      #change to ones() 
    p0Denom = 2.0; p1Denom = 2.0                        #change to 2.0

    sys.stdout.write('training  0.00%% now')
    for i in range(numTrainDocs):
        realVec = [0]*numWords
        # print trainMatrix[i],numWords
        for key in trainMatrix[i]:
            realVec[key] = trainMatrix[i][key]

        if trainCategory[i] == 1:
            p1Num += realVec
            p1Denom += sum(realVec)
        else:
            p0Num += realVec
            p0Denom += sum(realVec)

        sys.stdout.write('\b\b\b\b\b\b\b\b\b\b\b%6.2f%% now'%(float(i*100)/numTrainDocs))
        sys.stdout.flush()
    sys.stdout.write('\n')

    p1Vect = log(p1Num/p1Denom)          #change to log()
    p0Vect = log(p0Num/p0Denom)          #change to log()
    return p0Vect,p1Vect,pAbusive

def classifyNB(vec2Classify, p0Vec, p1Vec, pClass1):
    realVec = [0]*len(p0Vec)

    for key in vec2Classify:
        realVec[key] = vec2Classify[key]
    realVec = array(realVec)

    p1 = sum(realVec * p1Vec) + log(pClass1)    #element-wise mult
    p0 = sum(realVec * p0Vec) + log(1.0 - pClass1)
    if p1 > p0:
        return 1
    else: 
        return 0

def textParse(bigString, useJieba=True):    #input is big string, #output is word list

    if useJieba:
        # 引入jieba切词组件
        listOfTokens = jieba.cut(bigString)

    else:
        bigString = unicode(bigString)
        # 分离中英文，英文按单词处理，中文按单字处理
        listEn = re.split(r'[^a-zA-Z]*', bigString)
        listNum = re.split(r'[^0-9]*',bigString)
        listCn = re.split(r'(.)', re.sub(r'[\w|\s]*','',bigString))
        listOfTokens = listEn + listNum + listCn

    return [tok.lower() for tok in listOfTokens if len(tok) > 0] 

# 性能优化：returnVec由list变为dictionary，减小内存消耗
# inputSet由数组改为dictionary，使用has_key替代in，提升检索效率
def bagOfWords2VecMN(vocabList, inputSet):
    returnVec = {}
    # startTime = datetime.datetime.now()
    for word in inputSet:
        key = hashlib.md5(word).hexdigest()
        if vocabList.has_key(key) == 1:
            index = vocabList[key]["n"]
            if not returnVec.has_key(index):
                returnVec[index] = 1
            elif returnVec[index]<3:
                returnVec[index] += 1
    # print datetime.datetime.now() - startTime
    return returnVec

def loadTrainingSample():    
    docList=[]; classList = [];
    print 'loading Samples...'

    lines = open(config.spam_path).readlines()
    for line in lines:
        wordList = textParse(line)
        docList.append(wordList)
        # fullText.extend(wordList)
        classList.append(1)
    lines = open(config.ham_path).readlines()
    for line in lines:
        wordList = textParse(line)
        docList.append(wordList)
        # fullText.extend(wordList)
        classList.append(0)

    return docList, classList

def setSampleToMat(docList, classList, vocabList, trainingSet):
    trainMat=[]; trainClasses = []
    sys.stdout.write('SampleToMat finished:  0.00%')
    for docIndex in trainingSet:#train the classifier (get probs) trainNB0
        trainMat.append(bagOfWords2VecMN(vocabList, docList[docIndex]))
        trainClasses.append(classList[docIndex])

        sys.stdout.write('\b\b\b\b\b\b\b%6.2f%%'%(float(docIndex*100)/trainingSet[-1]))
        sys.stdout.flush()    
    sys.stdout.write('\n')

    return trainMat, trainClasses

def train():
    startTime = datetime.datetime.now()

    # 加载训练样本
    docList,classList = loadTrainingSample()

    # 创建词表
    vocabList = createVocabList(docList)#create vocabulary

    # 样本转换为向量    
    trainingSet = range(len(docList));          #create test set
    trainMat, trainClasses = setSampleToMat(docList, classList, vocabList, trainingSet)
    
    # 训练
    p0V,p1V,pSpam = trainNB0(array(trainMat),array(trainClasses),len(vocabList))

    #print vocabList
    f = open(config.vocabulary_path,'w')
    for key in vocabList:
        i = vocabList[key]["n"]
        f.writelines("%s\t%s\t%s\t%s\r\n"%(vocabList[key]["word"],p0V[i],p1V[i],pSpam))
    f.close

    print 'use time:%s'%(datetime.datetime.now()-startTime)


def spamTest():
    startTime = datetime.datetime.now()

    # 加载训练样本
    docList,classList = loadTrainingSample()

    # 创建词表
    print 'length of results is: %s'%len(docList)
    vocabList = createVocabList(docList)#create vocabulary
    print 'length of vocabList is: %s'%len(vocabList)

    #提取验证样本
    trainingSet = range(len(docList)); testSet=[]           #create test set
    for i in range(1000):
        randIndex = int(random.uniform(0,30000))
        testSet.append(trainingSet[randIndex])
        del(trainingSet[randIndex]) 

    # 样本转换为向量
    trainMat, trainClasses = setSampleToMat(docList, classList, vocabList, trainingSet)


    # 训练
    p0V,p1V,pSpam = trainNB0(array(trainMat),array(trainClasses),len(vocabList))
    print 'training finished.'

    # 测试验证
    errorCount = 0
    for docIndex in testSet:        #classify the remaining items
        wordVector = bagOfWords2VecMN(vocabList, docList[docIndex])
        if classifyNB(wordVector,p0V,p1V,pSpam) != classList[docIndex]:
            errorCount += 1
            print "classification error,right class is %s. "%classList[docIndex],string.join(docList[docIndex],'')
    print 'the error rate is: ',float(errorCount)/len(testSet)
    print 'use time:'
    print datetime.datetime.now()-startTime


def readDataFromFile():
    p0V = []; p1V = []; vocabList = {}
    lines = open(config.vocabulary_path).readlines()
    i = 0
    for line in lines:
        arrLine = re.split(r'\t',line)
        if len(arrLine)==4:
            key = hashlib.md5(arrLine[0]).hexdigest()
            vocabList[key] = {"n":i,"word":arrLine[0]}
            i += 1
            p0V.append(float(arrLine[1]))
            p1V.append(float(arrLine[2]))
    pSpam = float(re.split(r'\t',lines[0])[3])

    return vocabList,p0V,p1V,pSpam

def checkSpam(content):
    vocabList,p0V,p1V,pSpam = readDataFromFile()
    contentList = textParse(content)
    contentVector = bagOfWords2VecMN(vocabList, contentList)
    return classifyNB(contentVector,p0V,p1V,pSpam)


def runTrain():
    # 加入新样本
    if os.path.exists(config.train_spam_path):
        newSpamLines = open(config.train_spam_path).readlines()
        os.remove(config.train_spam_path)

        spamFile = open(config.spam_path,'a')
        spamFile.writelines(newSpamLines)
        spamFile.close()
    if os.path.exists(config.train_ham_path):
        newHamLines = open(config.train_ham_path).readlines()
        os.remove(config.train_ham_path)

        hamFile = open(config.ham_path,'a')
        hamFile.writelines(newHamLines)
        hamFile.close()

    # 开始训练
    train()