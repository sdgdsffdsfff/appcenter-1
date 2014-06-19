#encoding=UTF8
import main, hashlib
from flask.ext.login import UserMixin
from __header__ import AdminView, FlaskView
from __header__ import DB, route
from flask.ext.login import current_user
from functools import wraps
from flask import request, abort
from bson.objectid import ObjectId
import math

class View(FlaskView):
    route_base = '/dirty_word-manager'
    def before_request(self, name):
        self._view = AdminView()

class ListView(View):
    @route('/list', endpoint='admin_dirty_word_list')
    def get(self):
        NUM_PER_PAGE = 50
        count = DB.dirty_word.find().count()
        page_info = {"count": DB.dirty_word.find().count()}
        page = int(request.args.get('page', 1))
        page_info["total"] = int(math.ceil(count / float(NUM_PER_PAGE)))
        if page > page_info["total"] or page < 1: page = 1

        page_info["page"] = page
        dirty_word_list = DB.dirty_word.find().skip((page-1)*NUM_PER_PAGE).limit(NUM_PER_PAGE)
        return self._view.render('dirty_word_manage', dirty_word_list=list(dirty_word_list), page_info=page_info)

class AddView(View):
    @route('/add', methods=['POST'], endpoint='admin_dirty_word_add')
    def post(self):
        try:
            data = {
                'name': request.form['name']
            }
            DB.dirty_word.update({"name": request.form['name']}, data, True)
            status, message = 'success', '添加成功'
        except Exception, ex:
            status, message = 'error', str(ex.message)
        return self._view.ajax_response(status, message)

class DeleteView(View):
    @route('/delete', endpoint='admin_dirty_word_delete')
    def get(self):
        try:
            _id = request.args.get('_id')
            res = DB.dirty_word.remove({'_id': ObjectId(_id)})
            status, message = 'success', '删除成功'
        except Exception, ex:
            status, message = 'error', str(ex)
        return self._view.ajax_response(status, message)
