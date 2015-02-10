#encoding=UTF-8
#code by LP
#2013-11-27

import main
from flask import request
from __header__ import FlaskView, ApiView, route
from www.controller.app.global_config import GlobalConfigController

class View(FlaskView):
    route_base = '/global-config'

    def before_request(self, name):
        self._view = ApiView()
        self.global_config = GlobalConfigController()


class GloablConfigView(View):
    @route('/', endpoint='global_config')
    def get(self):
        data = self.global_config.get()
        return self._view.render(1000, data)
