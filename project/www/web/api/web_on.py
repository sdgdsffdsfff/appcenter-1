#encoding=UTF-8

import main
from flask import request
from __header__ import FlaskView, ApiView, route
from www.controller.app.header import mongo_db

class View(FlaskView):
    route_base = '/web_on/'

    def before_request(self, name):
        self._view = ApiView()

    def get_web_on_info(self):
        return mongo_db.web_on.find_one({}, {"_id": 0})

class WebOnView(View):
    @route('/info', endpoint='clinet_web_on')
    def get(self):
        jb = 1 - self._view._sign
        data = self.get_web_on_info()
        return self._view.render(1000, data)
