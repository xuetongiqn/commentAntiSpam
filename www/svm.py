#coding=utf-8

from numpy import *
import sys,datetime,string,re,os,jieba,linecache
import config

reload(sys)
sys.setdefaultencoding('utf8')

def selectJrand(i,m):
    j=i #we want to select any J not equal to i
    while (j==i):
        j = int(random.uniform(0,m))
    return j

def clipAlpha(aj,H,L):
    if aj > H: 
        aj = H
    if L > aj:
        aj = L
    return aj

def makeData(isTest=False):
    # 加载训练样本
    docList,classList = loadTrainingSample(isTest)

    newSampleList = []
    for line in docList:
        l, numCount, enCount, chCount, symbolCount, otherCount = analysisTxt(line)

        newSampleList.append([l, numCount*100/l, enCount*100/l, chCount*100/l, symbolCount*100/l, otherCount*100/l])
    
    return newSampleList, classList

def loadTrainingSample(isTest=False):
    docList=[]; classList = [];
    if isTest:
        lines = open('../data/svm_spam_test.txt').readlines()
    else:
        lines = open('../data/svm_spam.txt').readlines()
    for line in lines:
        docList.append(line)
        classList.append(1)

    if isTest:
        lines = open('../data/svm_ham_test.txt').readlines()
    else:
        lines = open('../data/svm_ham.txt').readlines()
    for line in lines:
        docList.append(line)
        classList.append(-1)

    return docList, classList


def analysisTxt(text):
    numCount=0;enCount=0;chCount=0;symbolCount=0;otherCount=0;
    l = len(text)
    
    for character in text:
        c_code = ord(character)
        if c_code >= 48 and c_code <= 57 :    #数字
            numCount = numCount + 1
        elif c_code >=65 and c_code <= 90 or c_code >=97 and c_code <= 122 :    #英文
            enCount = enCount + 1
        elif character in "`~\!@#\$%\^&\*\(\)\+=\|\{\}':;',\[\]\.<>\/\?~！@#￥%……（）——+【】‘；：”“’。，、？" :     #常用符号 
            symbolCount = symbolCount + 1
        elif c_code >= 19968 and c_code <= 40869 :  #中文\u4e00-\u9fa5
            chCount = chCount + 1
        else : 
            otherCount = otherCount + 1

    return l, numCount, enCount, chCount, symbolCount, otherCount

def kernelTrans(X, A, kTup): #calc the kernel or transform data to a higher dimensional space
    m,n = shape(X)
    K = mat(zeros((m,1)))
    if kTup[0]=='lin': K = X * A.T   #linear kernel
    elif kTup[0]=='rbf':
        for j in range(m):
            deltaRow = X[j,:] - A
            K[j] = deltaRow*deltaRow.T
        K = exp(K/(-1*kTup[1]**2)) #divide in NumPy is element-wise not matrix like Matlab
    else: raise NameError('Houston We Have a Problem -- That Kernel is not recognized')
    return K

class optStruct:
    def __init__(self,dataMatIn, classLabels, C, toler, kTup):  # Initialize the structure with the parameters 
        self.X = dataMatIn
        self.labelMat = classLabels
        self.C = C
        self.tol = toler
        self.m = shape(dataMatIn)[0]
        self.alphas = mat(zeros((self.m,1)))
        self.b = 0
        self.eCache = mat(zeros((self.m,2))) #first column is valid flag
        self.K = mat(zeros((self.m,self.m))) #MemoryError 3w*3w的矩阵服务器吃不消，用K()替代
        for i in xrange(self.m):
            self.K[:,i] = kernelTrans(self.X, self.X[i,:], kTup)
            sys.stdout.write("\b\b\b\b\b\b%6.0f"%i)
            sys.stdout.flush()
    #     f = open('_tmp_svm_matrix_K','w')
    #     tmp = ""
    #     for i in xrange(self.m):
    #         arr = kernelTrans(self.X, self.X[i,:], kTup)
    #         for j in arr:                
    #             tmp += '%s\n'%float(j)
    #         if i %100 == 0:
    #             f.writelines(tmp)
    #             tmp = ""
    #         sys.stdout.write("\b\b\b\b\b\b%6.0f"%i)
    #         sys.stdout.flush() 
    # # 时间换空间，内存吃紧，将大矩阵存为临时文件

    # def K(str):
    #     arrStr = str.split(',')
    #     arr = []
    #     if arrStr[0] == ":" :
    #         for i in xrange(self.m) :
    #             arr.append(self.K('%s:%s'%(i,arrStr[1])))
    #     elif arrstr[1] == ":" :
    #         for i in xrange(self.m) :
    #             arr.append(self.K('%s:%s'%(arrStr[0],i)))
    #     else:
    #         index = int(arrStr[0])*self.m + int(arrStr[1])
    #         return linecache.getline('_tmp_svm_matrix_K',index)

    #     return arr

        
def calcEk(oS, k):
    fXk = float(multiply(oS.alphas,oS.labelMat).T*oS.K[:,k] + oS.b)
    Ek = fXk - float(oS.labelMat[k])
    return Ek
        
def selectJ(i, oS, Ei):         #this is the second choice -heurstic, and calcs Ej
    maxK = -1; maxDeltaE = 0; Ej = 0
    oS.eCache[i] = [1,Ei]  #set valid #choose the alpha that gives the maximum delta E
    validEcacheList = nonzero(oS.eCache[:,0].A)[0]
    if (len(validEcacheList)) > 1:
        for k in validEcacheList:   #loop through valid Ecache values and find the one that maximizes delta E
            if k == i: continue #don't calc for i, waste of time
            Ek = calcEk(oS, k)
            deltaE = abs(Ei - Ek)
            if (deltaE > maxDeltaE):
                maxK = k; maxDeltaE = deltaE; Ej = Ek
        return maxK, Ej
    else:   #in this case (first time around) we don't have any valid eCache values
        j = selectJrand(i, oS.m)
        Ej = calcEk(oS, j)
    return j, Ej

def updateEk(oS, k):#after any alpha has changed update the new value in the cache
    Ek = calcEk(oS, k)
    oS.eCache[k] = [1,Ek]

def innerL(i, oS):
    Ei = calcEk(oS, i)
    if ((oS.labelMat[i]*Ei < -oS.tol) and (oS.alphas[i] < oS.C)) or ((oS.labelMat[i]*Ei > oS.tol) and (oS.alphas[i] > 0)):
        j,Ej = selectJ(i, oS, Ei) #this has been changed from selectJrand
        alphaIold = oS.alphas[i].copy(); alphaJold = oS.alphas[j].copy();
        if (oS.labelMat[i] != oS.labelMat[j]):
            L = max(0, oS.alphas[j] - oS.alphas[i])
            H = min(oS.C, oS.C + oS.alphas[j] - oS.alphas[i])
        else:
            L = max(0, oS.alphas[j] + oS.alphas[i] - oS.C)
            H = min(oS.C, oS.alphas[j] + oS.alphas[i])
        if L==H: print "L==H"; return 0
        eta = 2.0 * oS.K[i,j] - oS.K[i,i] - oS.K[j,j] #changed for kernel
        if eta >= 0: print "eta>=0"; return 0
        oS.alphas[j] -= oS.labelMat[j]*(Ei - Ej)/eta
        oS.alphas[j] = clipAlpha(oS.alphas[j],H,L)
        updateEk(oS, j) #added this for the Ecache
        if (abs(oS.alphas[j] - alphaJold) < 0.00001): print "j not moving enough"; return 0
        oS.alphas[i] += oS.labelMat[j]*oS.labelMat[i]*(alphaJold - oS.alphas[j])#update i by the same amount as j
        updateEk(oS, i) #added this for the Ecache                    #the update is in the oppostie direction
        b1 = oS.b - Ei- oS.labelMat[i]*(oS.alphas[i]-alphaIold)*oS.K[i,i] - oS.labelMat[j]*(oS.alphas[j]-alphaJold)*oS.K[i,j]
        b2 = oS.b - Ej- oS.labelMat[i]*(oS.alphas[i]-alphaIold)*oS.K[i,j]- oS.labelMat[j]*(oS.alphas[j]-alphaJold)*oS.K[j,j]
        if (0 < oS.alphas[i]) and (oS.C > oS.alphas[i]): oS.b = b1
        elif (0 < oS.alphas[j]) and (oS.C > oS.alphas[j]): oS.b = b2
        else: oS.b = (b1 + b2)/2.0
        return 1
    else: return 0

def smoP(dataMatIn, classLabels, C, toler, maxIter,kTup=('lin', 0)):    #full Platt SMO
    oS = optStruct(mat(dataMatIn),mat(classLabels).transpose(),C,toler, kTup)
    iter = 0
    entireSet = True; alphaPairsChanged = 0
    while (iter < maxIter) and ((alphaPairsChanged > 0) or (entireSet)):
        alphaPairsChanged = 0
        if entireSet:   #go over all
            for i in range(oS.m):        
                alphaPairsChanged += innerL(i,oS)
                print "fullSet, iter: %d i:%d, pairs changed %d" % (iter,i,alphaPairsChanged)
            iter += 1
        else:#go over non-bound (railed) alphas
            nonBoundIs = nonzero((oS.alphas.A > 0) * (oS.alphas.A < C))[0]
            for i in nonBoundIs:
                alphaPairsChanged += innerL(i,oS)
                print "non-bound, iter: %d i:%d, pairs changed %d" % (iter,i,alphaPairsChanged)
            iter += 1
        if entireSet: entireSet = False #toggle entire set loop
        elif (alphaPairsChanged == 0): entireSet = True  
        print "iteration number: %d" % iter
    return oS.b,oS.alphas


def spamTest(kTup=('rbf', 10)):
    sampleList, classList = makeData()
    #print len(sampleList), len(classList)
    b,alphas = smoP(sampleList, classList, 200, 0.0001, 10000, kTup)
    datMat=mat(sampleList); labelMat = mat(classList).transpose()
    svInd=nonzero(alphas.A>0)[0]
    sVs=datMat[svInd] 
    labelSV = labelMat[svInd];
    print "there are %d Support Vectors" % shape(sVs)[0]

    m,n = shape(datMat)
    errorCount = 0
    for i in range(m):
        kernelEval = kernelTrans(sVs,datMat[i,:],kTup)
        predict=kernelEval.T * multiply(labelSV,alphas[svInd]) + b
        if sign(predict)!=sign(classList[i]): errorCount += 1
    print "the training error rate is: %f" % (float(errorCount)/m)



    sampleList,classList = makeData(True)
    errorCount = 0
    datMat=mat(sampleList); labelMat = mat(classList).transpose()
    m,n = shape(datMat)
    for i in range(m):
        kernelEval = kernelTrans(sVs,datMat[i,:],kTup)
        predict=kernelEval.T * multiply(labelSV,alphas[svInd]) + b
        if sign(predict)!=sign(classList[i]): errorCount += 1    
    print "the test error rate is: %f" % (float(errorCount)/m) 