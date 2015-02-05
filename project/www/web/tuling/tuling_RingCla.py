#encoding=UTF-8
#code by LP
#2013-12-5

from __header__ import FlaskView, ApiView, route, request
from www.controller.tuling.tuling_RingCla import AppTopicController

class View(FlaskView):

    route_base = '/ring'
    def before_request(self, name):
        self._view = ApiView()
        self.app_tuling = AppTopicController(self._view._language, self._view._ip)

class ListView(View):
    @route('/list', endpoint='tuling_RingCla_list')
    def get(self):
        
	category_language = request.args.get('category_language', 'EN')

        res = self.app_tuling.get_list(category_language)
			
        return self._view.render(1000, res)
