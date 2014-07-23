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
    route_base = '/other-ad-manager'
    def before_request(self, name):
        self._view = AdminView()

class ListView(View):
    @route('/list', endpoint='admin_other_ad_list')
    def get(self):
        other_ad_list = DB.other_ad.find()
        return self._view.render('other_ad_manage', other_ad_list=list(other_ad_list))

class EditView(View):
    @route('/edit', methods=['POST'], endpoint='admin_other_ad_edit')
    def post(self):
        try:
            data = {
                'cs': request.form['cs'],
                'language': request.form['language'],
                'login_ad_status': request.form["login_ad_status"],
                'position_ad_status': request.form["position_ad_status"]
            }
            DB.other_ad.update({"cs": request.form['name']}, data, True)
            status, message = 'success', '添加成功'
        except Exception, ex:
            status, message = 'error', str(ex.message)
        return self._view.ajax_response(status, message)
