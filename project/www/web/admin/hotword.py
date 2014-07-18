#encoding=UTF8
import math

from flask import request, abort
from bson.objectid import ObjectId

import main
from __header__ import AdminView, FlaskView
from __header__ import DB, route


class View(FlaskView):
    route_base = '/hotword-manager'
    def before_request(self, name):
        self._view = AdminView()

class ListView(View):
    @route('/list', endpoint='admin_hotword_list')
    def get(self):
        NUM_PER_PAGE = 50
        count = DB.hot_word.find().count()
        page_info = {"count": count}
        page = int(request.args.get('page', 1))
        page_info["total"] = int(math.ceil(count / float(NUM_PER_PAGE)))
        if page > page_info["total"] or page < 1: page = 1
        page_info["page"] = page
        hotword_list = DB.hot_word.find().sort("order", -1).skip((page-1)*NUM_PER_PAGE).limit(NUM_PER_PAGE)
        #get the support country
        lang_options = []
        [lang_options.append((lang['name'],lang['code'])) for lang in DB.client_support_language.find()]
        return self._view.render('hotword_manage', hotword_list=list(hotword_list), 
                                 page_info=page_info,lang_options=lang_options)


class AddView(View):
    @route('/add', methods=['POST'], endpoint='admin_hotword_add')
    def post(self):
        try:
            data = {
                'name': request.form['name'],
                'order': int(request.form["order"]),
                "device": request.form.getlist("device"),
                "language": request.form.getlist("language")
            }
            DB.hot_word.update({"name": request.form['name']}, data, True)
            status, message = 'success', '添加成功'
        except Exception, ex:
            status, message = 'error', str(ex.message)
        return self._view.ajax_response(status, message)


class DeleteView(View):
    @route('/delete', endpoint='admin_hotword_delete')
    def get(self):
        try:
            _id = request.args.get('_id')
            res = DB.hot_word.remove({'_id': ObjectId(_id)})
            status, message = 'success', '删除成功'
        except Exception, ex:
            status, message = 'error', str(ex)
        return self._view.ajax_response(status, message)
