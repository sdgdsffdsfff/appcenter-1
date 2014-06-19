# -*- coding: utf-8 -*-
# Created by pengchangliang on 14-3-15.

import cjson
from flask import request
from common.web.app import WebApp, create_url

class WebSiteBase(WebApp):

    def before(self):
        self._language = 'ZH'
        pass

    def ajax_response(self, status, message='', data={}):
        data = {'status':status, 'message':message, 'data':data}
        return cjson.encode(data)

    def ajax_render(self, tpl, **kwargs):
        tpl_data = self.render(tpl, **kwargs)
        data = {'status':'success', 'message':'', 'data':tpl_data}
        return cjson.encode(data)

    def error(self, msg, back=''):
        return self.render('error', msg=msg, back=back)