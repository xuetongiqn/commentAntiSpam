#coding=utf-8

import web,re,sys,memcache,hashlib
reload(sys)
sys.setdefaultencoding('utf8')

def checkSpam(content, qid, itemId):
    key = hashlib.md5(qid + '_' + itemId + '_' + content.strip()).hexdigest()

    mc = memcache.Client(['w-mc03.add.zwt.qihoo.net:9119'])

    if mc.get(key)=='1':
        return 1
    else:
        mc.set(key,'1',86400) #保存1天
        return 0
        