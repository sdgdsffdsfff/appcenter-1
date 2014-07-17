#encoding=UTF-8
#code by LP
#2013-11-4

from __header__ import FlaskView, ApiView, route, request
from www.controller.app.language import LanguageController

class View(FlaskView):

    route_base = '/language'

    def before_request(self, name):
        self._view = ApiView()


class ListView(View):
    @route('/list', endpoint='api_language_list')
    def get(self):
        languages = LanguageController().get()
        return self._view.render(1000, languages)
