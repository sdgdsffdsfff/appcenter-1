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
    route_base = '/download-batch-manager'
    def before_request(self, name):
        self._view = AdminView()

class ListView(View):
    @route('/list', endpoint='admin_vshare_version_list')
    def get(self):
        vshare_version_list = DB.vshare_version.find()
        return self._view.render('download_batch', vshare_version_list=list(vshare_version_list))

class AddView(View):
    @route('/add', methods=['POST'], endpoint='admin_vshare_version_add')
    def post(self):
        try:
            data = {
                'identity': request.form['identity'],
                'name': request.form['name'],
                'apple_account': request.form["apple_account"]
            }
            DB.vshare_version.update({"name": request.form['name']}, data, True)
            status, message = 'success', '添加成功'
        except Exception, ex:
            status, message = 'error', str(ex.message)
        return self._view.ajax_response(status, message)

class DeleteView(View):
    @route('/delete', endpoint='admin_vshare_version_delete')
    def get(self):
        try:
            _id = request.args.get('_id')
            res = DB.vshare_version.remove({'_id': ObjectId(_id)})
            status, message = 'success', '删除成功'
        except Exception, ex:
            status, message = 'error', str(ex)
        return self._view.ajax_response(status, message)

class EditView(View):
    @route('/edit', methods=['POST'], endpoint='admin_vshare_version_edit')
    def post(self):
        try:
            data = {
                'identity': request.form['identity'],
                'name': request.form['name'],
                'apple_account': request.form["apple_account"]
            }
            _id = request.form["_id"]
            DB.vshare_version.update({"_id": ObjectId(_id)}, {"$set": data})
            status, message = 'success', '修改成功'
        except Exception, ex:
            status, message = 'error', str(ex.message)
        return self._view.ajax_response(status, message)
