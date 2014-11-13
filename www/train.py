#coding=utf-8

import web,re,datetime,json
import config


urls = (

    "", "train"

)


class train:
    def __init__(self,):
        self.logger = web.ctx.environ['wsgilog.logger']

    def GET(self):
        #time1 = datetime.datetime.now()

        content = web.input().get('content',"")
        isSpam = web.input().get('spam','')

        saveTrainList(content,isSpam)

        self.logger.info('{isSpam:"%s",content:"%s"}'%(isSpam,content))

        return json.JSONEncoder().encode({'errno':'0'})

    def POST(self):
        content = web.input().get('content',"")
        isSpam = web.input().get('spam','')

        saveTrainList(content,isSpam)

        self.logger.info('{isSpam:"%s",content:"%s"}'%(isSpam,content))

        return json.JSONEncoder().encode({'errno':'0'})

def saveTrainList(content,isSpam):
    content = re.sub('[\r|\n]','',content)

    if isSpam == '1':
        f = open(config.train_spam_path,'a')
        f.writelines(content+"\n")
        f.close()
    elif isSpam == '0':
        f = open(config.train_ham_path,'a')        
        f.writelines(content+"\n")
        f.close()




app_train = web.application(urls,locals())
