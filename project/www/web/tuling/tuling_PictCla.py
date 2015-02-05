#encoding=UTF-8
#code by LP
#2013-12-5

from __header__ import FlaskView, ApiView, route, request
from www.controller.tuling.tuling_PictCla import AppTopicController

class View(FlaskView):

    route_base = '/picture'
    def before_request(self, name):
        self._view = ApiView()
        self.app_tuling = AppTopicController(self._view._language, self._view._ip)

class ListView(View):
    @route('/list', endpoint='tuling_PictCla_list')
    def get(self):
        res = self.app_tuling.get_list()
        return self._view.render(1000, res)
