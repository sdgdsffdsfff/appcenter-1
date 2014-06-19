#encoding=UTF8
import hashlib
from functools import wraps

from flask.ext.login import UserMixin
from flask.ext.login import current_user
from flask import request, abort
from bson.objectid import ObjectId

import main
from __header__ import AdminView, FlaskView
from __header__ import DB, route


class View(FlaskView):
    route_base = '/clienttype-manager'
    def before_request(self, name):
        self._view = AdminView()

class ListView(View):
    @route('/list', endpoint='admin_clienttype_list')
    def get(self):
        clienttype_list = DB.client_type.find()
        return self._view.render('clienttype_manage', clienttype_list=list(clienttype_list))

class AddView(View):
    @route('/add', methods=['POST'], endpoint='admin_clienttype_add')
    def post(self):
        try:
            data = {
                'name': request.form['name'],
                'type_id': request.form["type_id"],
                'ipaname': request.form["ipaname"]
            }
            DB.client_type.update({"name": request.form['name']}, data, True)
            status, message = 'success', '添加成功'
        except Exception, ex:
            status, message = 'error', str(ex.message)
        return self._view.ajax_response(status, message)

class DeleteView(View):
    @route('/delete', endpoint='admin_clienttype_delete')
    def get(self):
        try:
            _id = request.args.get('_id')
            res = DB.client_type.remove({'_id': ObjectId(_id)})
            status, message = 'success', '删除成功'
        except Exception, ex:
            status, message = 'error', str(ex)
        return self._view.ajax_response(status, message)
