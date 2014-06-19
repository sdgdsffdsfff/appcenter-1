#encoding=UTF-8
#code by LP
#2013-12-5

from __header__ import FlaskView, ApiView, route, request
from www.controller.app.app_topic import AppTopicController

class View(FlaskView):

    route_base = '/app_topic'

    def before_request(self, name):
        self._view = ApiView()
        self.app_topic = AppTopicController(self._view._language, self._view._ip)


class DetailView(View):

    @route('/detail', endpoint='api_app_topic_detail')
    def get(self):
        object_id = request.args.get('id', None)
        if object_id is None:
            self._view.render_error('error')
        res = self.app_topic.get(object_id, front=True)
        return self._view.render(1000, res)


class ListView(View):

    @route('/list', endpoint='api_app_topic_list')
    def get(self):
        res = self.app_topic.get_list()
        return self._view.render(1000, res)
