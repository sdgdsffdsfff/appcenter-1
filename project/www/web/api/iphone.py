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

    route_base = '/iphone'

    def before_request(self, name):
        self._view = ApiView()
        self.app = AppController(language=self._view._language)

    def _get_advertising(self, identifier):
        ad = AdvertisingController(identifier, self._view._language, self._view._ip)
        return ad.get(5)

    def _get_app_collection(self, identifier, jb):
        col = AppCollectionController(identifier, language=self._view._language, ip=self._view._ip, country=self._view._country)
        return col.get(num=30, front=True)

    def _get_app_topic(self, jb):
        topic = AppTopicController(self._view._language, self._view._ip)
        return topic.get_list(jb)


class HomePageView(View):
    """
    iphone home page feture
    """
    @route('/home_page', endpoint='api_iphone_home_page')
    def get(self):
        data = {}
        jb = request.args.get("jb", 0)
        #滚动幻灯片
        data['slider'] = self._get_advertising('iphone_index_flash')
        #今日推荐
        if int(jb) == 0:
            data['apps'] = self._get_app_collection('iphone_index_app_list')
        else:
            data['apps'] = self._get_app_collection('iphone_index_app_list_jb')
        #topic
        data['topic'] = self._get_app_topic(int(jb))
        return self._view.render(1000, data)

# class HomeAdImageView(View):
#     @route('/home_ad_image', endpoint='api_home_ad_image')
#     def get(self):
#         data = {}
#         data['ad_images'] = self._get_advertising('iphone_index_flash')
#         return self._view.render(1000, data)
