#encoding=UTF-8
#code by LP
#2013-11-27

import time
import cjson
import json
import types
from flask import request, make_response

from conf.settings import settings
from www.web.base import WebView
from flask.ext.classy import FlaskView, route
from flask import redirect, session, request, url_for

from xml.etree.ElementTree import Element, SubElement, ElementTree
import xml.etree.ElementTree as ET
from xml.dom import minidom


class ApiView(WebView):

    def __init__(self):
        self.request_start_time = time.time()
        super(ApiView, self).__init__(__file__)
        #语言
        self._language = request.args.get('language', 'EN')
        #ip
        self._ip = request.remote_addr
        #国家
        self._country = request.args.get('country', None)
        #渠道包类型
        self._client_type = request.args.get('country', 'jb')
        #用于判断签名和越狱
        try:
            self._sign = 1 - int(request.args.get('jb', 1))
        except:
            self._sign = 0

    def render(self, code, data, status_code=200, output_format=None):

        ''' 按格式输出数据 '''
        #执行时间
        exec_time = time.time() - self.request_start_time

        data = {'code':int(code), 'time':exec_time, 'data':data}
        if output_format != None:
            response_format = output_format
        else:
            response_format = self.__get_format_from_headers(request.headers['Accept'])

        if response_format == 'xml':
            response = make_response(self.__dict2xmlstring('root', data))
            response.headers['Content-Type'] = 'application/xml'
        else:
            response = make_response(json.dumps(data))
            response.headers['Content-Type'] = 'application/json'

        return response, status_code

    def render_error(self, msg, status_code=200, code=0):
        ''' 错误输出 '''
        return self.render(code, msg, status_code)

    def __get_format_from_headers(self, headers):
        ''' 获取请求的格式 '''
        try:
            return re.findall("application\/(json)", headers)[0]
        except:
            return 'json'

    def __dict2xmlstring(self, root, data):
        ''' dict转xml '''

        et = dict2xml('root', data)
        return minidom.parseString(ET.tostring(et, encoding='utf-8', method='xml')).toprettyxml()


def dict2xml(root, content):

    ''' dict转xml '''

    if type(content) != types.ListType and type(content) != types.TupleType and type(content) != types.DictType:
        e = Element(root)
        e.text = str(content)
        return e
    e = Element(root)
    for key in content:
        if type(content[key]) == list:
            for one in content[key]:
                e.append(dict2xml(key,one))
        else:
            e.append(dict2xml(key,content[key]))
    return e
