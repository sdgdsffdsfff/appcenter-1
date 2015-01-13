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
    route_base = '/adslink-manager'
    def before_request(self, name):
        self._view = AdminView()

class ListView(View):
    @route('/list', endpoint='admin_adslink_list')
    def get(self):
        adslink_list = DB.adslink.find()
        return self._view.render('adslink_manage', adslink_list=list(adslink_list))

class AddView(View):
    @route('/add', methods=['POST'], endpoint='admin_adslink_add')
    def post(self):
        try:
            data = {
                'edit_id': request.form['edit_id'],
                'bundle_id': request.form['bundle_id'],
                'url': request.form["url"]
            }
            DB.adslink.update({"bundle_id": request.form['bundle_id']}, data, True)
            status, message = 'success', '添加成功'
        except Exception, ex:
            status, message = 'error', str(ex.message)
        return self._view.ajax_response(status, message)

class DeleteView(View):
    @route('/delete', endpoint='admin_adslink_delete')
    def get(self):
        try:
            _id = request.args.get('_id')
            res = DB.adslink.remove({'_id': ObjectId(_id)})
            status, message = 'success', '删除成功'
        except Exception, ex:
            status, message = 'error', str(ex)
        return self._view.ajax_response(status, message)
