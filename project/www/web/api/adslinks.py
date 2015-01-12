#encoding=UTF-8
#code by LP
#2013-11-27

import main
from flask import request
from __header__ import FlaskView, ApiView, route
from www.controller.app.adslinks import AdsLinkController

class View(FlaskView):
    route_base = '/adslink'

    def before_request(self, name):
        self._view = ApiView()
        self.adslink_con = AdsLinkController()

    def _get_adslink(self):
        col = AdsLinkController()
        return col.get()


class AdsLinkView(View):
    @route('/', endpoint='get_ads_link')
    def get(self):
        data = {}
        data['adslink'] = self._get_adslink()
        return self._view.render(1000, data)
