#coding=utf-8

import web
import checkspam,train,sys

reload(sys)
sys.setdefaultencoding('utf8')

urls = (
    '/checkspam', checkspam.app_checkspam,
    '/train', train.app_train,
    '/','index',
)


class index:
    def __init__(self,):
        self.logger = web.ctx.environ['wsgilog.logger'] # 使用日志 #

    def GET(self):
        #self.logger.info('asdf')
        return 'status ok'


if __name__ == "__main__":
    from log import Log
    # print Log
    app = web.application(urls,globals())
    app.run(Log)
