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
    route_base = '/country-manager'
    def before_request(self, name):
        self._view = AdminView()

class ListView(View):
    @route('/list', endpoint='admin_country_list')
    def get(self):
        country_list = DB.country.find()
        return self._view.render('country_manage', country_list=list(country_list))

class AddView(View):
    @route('/add', methods=['POST'], endpoint='admin_country_add')
    def post(self):
        try:
            data = {
                'code': request.form['code'],
                'name': request.form['name'],
                'nameofcountry': request.form["nameofcountry"]
            }
            DB.country.update({"name": request.form['name']}, data, True)
            status, message = 'success', '添加成功'
        except Exception, ex:
            status, message = 'error', str(ex.message)
        return self._view.ajax_response(status, message)

class DeleteView(View):
    @route('/delete', endpoint='admin_country_delete')
    def get(self):
        try:
            _id = request.args.get('_id')
            res = DB.country.remove({'_id': ObjectId(_id)})
            status, message = 'success', '删除成功'
        except Exception, ex:
            status, message = 'error', str(ex)
        return self._view.ajax_response(status, message)
