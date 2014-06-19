#encoding=UTF-8
#code by LP
#2013-11-4

from header import *

from controller.vshare.app import AppController


class Base(WebSiteBase):

    def before(self):
        super(Base, self).before()


class Index(WebSiteBase):
    '''
    通过bundleid获取应用
    '''
    def GET(self):

        return self.render('index')
