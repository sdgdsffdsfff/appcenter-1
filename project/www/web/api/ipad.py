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

    route_base = '/ipad'

    def before_request(self, name):
        self._view = ApiView()
        self.app = AppController(language=self._view._language)

    def _get_advertising(self, identifier):
        ad = AdvertisingController(identifier, self._view._language, self._view._ip)
        return ad.get(5)

    def _get_app_collection(self, identifier):
        col = AppCollectionController(identifier, language=self._view._language, ip=self._view._ip, country=self._view._country)
        return col.get(num=30, front=True, sign=self._view._sign)



class HomePageView(View):
    """
    iphone home page feture
    """
    @route('/home_page', endpoint='api_ipad_home_page')
    def get(self):
        data = {}
        jb = request.args.get("jb", 0)
        if int(jb) == 0:
            collection_name = 'ipad_index_app_list'
            advertising_name = 'ipad_index_flash'
        else:
            collection_name = 'ipad_index_app_list_jb'
            advertising_name = 'ipad_index_flash_jb'
        if self._view.ifo == 0:
            collection_name += "_first"
            advertising_name += "_first"
        data['apps'] = self._get_app_collection(collection_name)
        data['slider'] = self._get_advertising(advertising_name)
        return self._view.render(1000, data)
