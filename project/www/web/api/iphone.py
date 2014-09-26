#encoding=UTF-8
#code by LP
#2013-11-27

import main
from flask import request
from __header__ import FlaskView, ApiView, route
from www.controller.app.app import AppController
from www.controller.app.advertising import AdvertisingController
from www.controller.app.app_collection import AppCollectionController
from www.controller.app.app_topic import AppTopicController
from conf.settings import CACHE_TIME

class View(FlaskView):

    route_base = '/iphone'

    def before_request(self, name):
        self._view = ApiView()
        self.app = AppController(language=self._view._language)

    def _get_advertising(self, identifier):
        ad = AdvertisingController(identifier, self._view._language, self._view._ip)
        return ad.get(5)

    def _get_app_collection(self, identifier):
        col = AppCollectionController(identifier, language=self._view._language, ip=self._view._ip, country=self._view._country)
        return col.get(num=30, front=True)

    def _get_app_topic(self, jb):
        topic = AppTopicController(self._view._language, self._view._ip)
        return topic.get_list(jb)


class HomePageView(View):
    """iphone home page feture"""
    @route('/home_page', endpoint='api_iphone_home_page')
    @main.cache.cached(timeout=CACHE_TIME, key_prefix='view/%(request.path)s?%(request.query_string)s')
    def get(self):
        data = {}
        jb = 1 - self._view._sign
        collection_name = 'iphone_index_app_list' if self._view._sign else 'iphone_index_app_list_jb'
        advertising_name = 'iphone_index_flash' if self._view._sign else 'iphone_index_flash_jb'
        data['apps'] = self._get_app_collection(collection_name)
        data['slider'] = self._get_advertising(advertising_name)
        data['topic'] = self._get_app_topic(int(jb))
        return self._view.render(1000, data)
