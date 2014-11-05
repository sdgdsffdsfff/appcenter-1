#encoding=UTF-8
#code by LP
#2013-11-27

import main
from flask import request
from __header__ import FlaskView, ApiView, route
from www.controller.app.app import AppController
from www.controller.app.app_collection import AppCollectionController

class View(FlaskView):
    route_base = '/app_collection'

    def before_request(self, name):
        self._view = ApiView()
        self.app = AppController(language=self._view._language)

    def _get_app_collection(self, identifier):
        col = AppCollectionController(identifier, language=self._view._language, ip=self._view._ip, country=self._view._country)
        return col.get(num=50, front=True, sign=self._view._sign)


class AppListView(View):
    @route('/apps_for_collection', endpoint='apps_for_collection')
    def get(self):
        collection_name = request.args.get("collection_name", "")
        data = {}
        data['apps'] = self._get_app_collection(collection_name)
        return self._view.render(1000, data)
