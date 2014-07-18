#encoding=UTF-8

from __header__ import FlaskView, ApiView, route, request
from www.controller.app.app_hotword import AppHotWordController

class View(FlaskView):

    route_base = '/hot_word'

    def before_request(self, name):
        self._view = ApiView()


class ListView(View):

    @route('/list', endpoint='api_hotword_list')
    def get(self):
        language = request.args.get('language', "EN")
        device = request.args.get("device", "1")
        hotwords = AppHotWordController(language, device)
        data = hotwords.get_list()
        return self._view.render(1000, data)