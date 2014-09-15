#encoding=UTF-8
#code by LP
#2013-11-27

from flask import request
from __header__ import FlaskView, ApiView, route
from www.controller.app.app import AppController
from www.controller.app.advertising import AdvertisingController
from www.controller.app.app_collection import AppCollectionController
from www.controller.app.app_topic import AppTopicController


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
        return col.get(num=30, front=True)



class HomePageView(View):
    """
    iphone home page feture
    """
    @route('/home_page', endpoint='api_ipad_home_page')
    def get(self):
        data = {}
        jb = request.args.get("jb", 0)
        #今日推荐|#滚动幻灯片
        if int(jb) == 0:
            data['apps'] = self._get_app_collection('ipad_index_app_list')
            data['slider'] = self._get_advertising('ipad_index_flash')
        else:
            data['apps'] = self._get_app_collection('ipad_index_app_list_jb')
            data['slider'] = self._get_advertising('ipad_index_flash_jb')
        return self._view.render(1000, data)
