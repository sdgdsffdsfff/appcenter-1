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
    route_base = '/apple-account-manager'
    def before_request(self, name):
        self._view = AdminView()

class ListView(View):
    @route('/list', endpoint='apple_account_list')
    def get(self):
        country_list = DB.country.find()
        return self._view.render('apple_account_manage')
