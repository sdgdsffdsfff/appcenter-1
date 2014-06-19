#encoding=UTF8
#code by LP
#2013-12-2

import json
from www.controller.app.app import AppController
from __header__ import AdminView, FlaskView, DB, redis_master, route, request, session, redirect, url_for

class View(FlaskView):

    route_base = '/cache'

    def before_request(self, name):
        self._view = AdminView()


class InfoView(View):

    @route('/info', endpoint='admin_cache_app_info')
    def get(self):
        return self._view.render('cache_status')

    @route('/info/status', endpoint='admin_cache_app_info_status')
    def get_status(self):
        app = AppController()
        data = {
            'cached_appinfo_count': app.get_cached_appinfo_count('EN'),
            'cached_appversion_count': app.get_cached_appversion_count('EN')
        }
        return self._view.ajax_response('success', '', data)