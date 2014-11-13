#coding=utf-8

import web,re,datetime,json

urls = (

    "", "checkspam"

)


# 关键词命中方式进行作弊判断
def getContentLevel(content, qid, itemId):
    levelMap = {
        "0" : "通过",
        "1" : "关键词屏蔽",
        "2" : "含有url",
        "3" : "机器学习屏蔽",
        "4" : "发帖频率控制"
    }

    q2bContent = strQ2B(content)

    # 关键词屏蔽
    import keywords
    if keywords.checkSpam(q2bContent) != 0:
        return 1,levelMap['1']

    
    # url地址过滤
    if re.search(r'[0-9a-zA-Z\-]+\.[a-zA-Z]{2,}',q2bContent):
        return 2,levelMap['2']

    # 机器学习
    import ml
    if len(content)>8 and ml.checkSpam(content)==1:
        return 3,levelMap['3']

    # 频率控制
    import frequency
    if frequency.checkSpam(q2bContent, qid, itemId) == 1:
        return 4,levelMap['4']


    return 0, levelMap['0']




class checkspam:
    def __init__(self,):
        self.logger = web.ctx.environ['wsgilog.logger']

    def GET(self):
        return self._doCheckSpam()

    def POST(self):
        return self._doCheckSpam()


    def _doCheckSpam(self):
        time1 = datetime.datetime.now()
        data = web.input()
        content = data.get('content',"")
        qid = data.get('qid',"")
        itemId = data.get('item_id',"")

        level,levelmsg = getContentLevel(content, qid, itemId)
        ip = web.ctx.env.get('REMOTE_ADDR','')

        spendTime = datetime.datetime.now() - time1
        self.logger.info('{level:"%s",content:"%s",qid:"%s",item_id:"%s",useTime:"%s",post_ip:"%s"}'%(level,content,qid,itemId,spendTime,ip))
        return json.JSONEncoder().encode({'errno':'0','level':level,'levelmsg':levelmsg})



#"""全角转半角"""
def strQ2B(ustring):
    rstring = ""
    for uchar in ustring:
        inside_code=ord(uchar)
        if inside_code == 12288:                              #全角空格直接转换            
            inside_code = 32 
        elif (inside_code >= 65281 and inside_code <= 65374): #全角字符（除空格）根据关系转化
            inside_code -= 65248

        rstring += unichr(inside_code)
    return rstring













app_checkspam = web.application(urls,locals())
