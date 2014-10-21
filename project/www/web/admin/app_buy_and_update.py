#encoding=UTF8
import main, hashlib
from flask.ext.login import UserMixin
from __header__ import AdminView, FlaskView
from __header__ import DB, route
from flask.ext.login import current_user
from functools import wraps
from flask import request, abort
from bson.objectid import ObjectId

class View(FlaskView):
    route_base = '/app-buy-manager'
    def before_request(self, name):
        self._view = AdminView()

class ListView(View):
    @route('/list', endpoint='app_buy')
    def get(self):
        return self._view.render('app_buy_manage')

class UpdateListView(View):
    @route('/update_list', endpoint='app_update')
    def get(self):
        return self._view.render('app_update_manage')

class AllListView(View):
    @route('/all_list', endpoint='app_all')
    def get(self):
        return self._view.render('app_all_manage')

class GetTaskView(View):
    @route('/get-task', endpoint='get_buy_task')
    def get(self):
        track_id = "623592465"
        track_name = "Heads Up!"
        version = "2.3.5"
        price = 19
        currency = "USD"
        link_url = "https://itunes.apple.com/app/id623592465"
        new_app_task = {
            "track_id": track_id,
            "track_name": track_name,
            "new_version": version,
            "price": price,
            "link_url": link_url,
            "currency": currency,
            "status": "new",
        }
        DB.new_app_task.insert(new_app_task)
        return self._view.ajax_response(200, new_app_task)
