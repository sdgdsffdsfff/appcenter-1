#encoding=UTF8
import re
import main, hashlib
from flask.ext.login import UserMixin
from __header__ import AdminView, FlaskView, session
from __header__ import DB, route, redirect, url_for
from flask.ext.login import current_user
from functools import wraps
from flask import request, abort
from bson.objectid import ObjectId
# from www.lib.form import Form, FormValidatorAbstract

class View(FlaskView):
    route_base = '/apple-account-manager'
    def before_request(self, name):
        self._view = AdminView()


class ListView(View):
    @route('/list', endpoint='apple_account_list')
    def get(self):
        account_list, country_list = [], []
        try:
            country_list = DB.country.find()
            userid = DB.User.find_one({"username": current_user.username})['_id']
            account_list = DB.apple_account.find({"user_id": userid})
        except Exception, ex:
            status, message = 'error', str(ex.message)
        # account_list = DB.apple_account.find()
        return self._view.render('apple_account_manage',
                                 country_list=country_list,
                                 account_list=account_list)


class AddView(View):
    @route('/add', methods=['POST'], endpoint='apple_account_add')
    def post(self):
        if 'acid' in request.form:
            acid = request.form['acid']
        else:
            acid = ''
        try:
            userid = DB.User.find_one({"username": current_user.username})['_id']
        except Exception, ex:
            status, message = 'error', str(ex.message)
            return self._view.ajax_response(status, message)
        try:
            data = {
                'country': request.form['country'],
                'apple_account': request.form['apple_account'],
                'email_passwd': request.form['email_passwd'],
                'itunes_passwd': request.form['itunes_passwd'],
                'itunes_sec1': request.form['itunes_sec1'],
                'itunes_sec2': request.form['itunes_sec2'],
                'itunes_sec3': request.form['itunes_sec3'],
                'status': request.form['status'],
                'balance': float(request.form['balance']),
                'user_id': userid
            }
            email_pattern = '^[a-zA-Z](\\w*[-_]?\\w+)*@(\\w*[-_]?\\w+)+[\\.][a-zA-Z]{2,3}([\\.][a-zA-Z]{2})?$'
            if not re.search(email_pattern, data['apple_account']):
                status = 'error'
                message = '注册帐号格式不正确'
                return self._view.ajax_response(status, message)
            if acid:
                user_had = DB.apple_account.find_one({'apple_account': data['apple_account'], '_id': {'$ne': ObjectId(acid)}})
            else:
                user_had = DB.apple_account.find_one({'apple_account': data['apple_account']})
            if user_had:
                username = DB.User.find_one({'_id': ObjectId(user_had['user_id'])})['username']
                status = 'error'
                message = '%s 已经拥有这个账户' % str(username)
                return self._view.ajax_response(status, message)
            if acid:
                res = DB.apple_account.find_one({'_id': ObjectId(acid)})
                DB.apple_account.update({'_id': ObjectId(acid)}, data)
                status, message = 'success', '添加成功'
            else:
                DB.apple_account.insert(data)
                status, message = 'success', '添加成功'
        except Exception, ex:
            status, message = 'error', str(ex.message)
        return self._view.ajax_response(status, message)


class DeleteView(View):
    @route('/delete', endpoint='apple_account_delete')
    def get(self):
        try:
            _id = request.args.get('id')
            DB.apple_account.remove({'_id': ObjectId(_id)})
            status, message = 'success', '删除成功'
        except Exception, ex:
            status, message = 'error', str(ex.message)
        return self._view.ajax_response(status, message)
