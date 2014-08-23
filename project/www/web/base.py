# -*- coding: utf-8 -*-
# Created by pengchangliang on 14-4-9.

import os
import cjson, json
from flask import render_template
from bson.json_util import dumps


class WebView(object):

    def __init__(self, header_file):
        self._template_folder = os.path.dirname(header_file).split(os.path.sep)[-1]
        self._assign_vars = {}

    def ajax_response(self, status, message='', data={}):
        data = {'status': status, 'message': message, 'data': data}
        try:
            return json.dumps(data)
        except TypeError:
            return dumps(data)

    def ajax_render(self, template, **kwargs):
        tpl_data = self.render(template, **kwargs)
        data = {'status': 'success', 'message': '', 'data': tpl_data}
        return cjson.encode(data)

    def error(self, msg, back=''):
        return self.render('error', msg=msg, back=back)

    def assign(self, key, value):
        try:
            self._assign_vars[key] = value
        except:
            self._assign_vars = {key: value}

    def render(self, template, *args, **kwargs):

        try:
            kwargs.update(self._assign_vars)
        except:
            pass
        return render_template(self._template_folder+'/'+template+'.html', *args, **kwargs)

    def render_error(self, msg, status_code=200):

        return '<html><head><title>%s</title></head><body>%s<body></html>' % (msg, msg)
