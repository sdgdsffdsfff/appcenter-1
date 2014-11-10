#encoding=UTF-8

from __header__ import FlaskView, ApiView, route, request
from www.controller.app.notification import NotificationController

class View(FlaskView):

    route_base = '/notification'

    def before_request(self, name):
        self._view = ApiView()


class ListView(View):

    @route('/list', endpoint='api_notification_list')
    def get(self):
        '''here we keep the language and device TODO'''
        language = request.args.get('language', "EN")
        device = request.args.get("device", "1")
        noti = NotificationController()
        data = noti.get_list()
        return self._view.render(1000, data)