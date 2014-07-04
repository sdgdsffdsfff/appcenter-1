#encoding=UTF8
import math

from flask import request, abort
from bson.objectid import ObjectId

import main
from __header__ import AdminView, FlaskView
from __header__ import DB, route



class View(FlaskView):
    route_base = '/search-q-manager'
    def before_request(self, name):
        self._view = AdminView()

class ListView(View):
    @route('/list', endpoint='admin_search_list')
    def get(self):
        NUM_PER_PAGE = 50
        count = DB.search_q.find({"count": 0}).count()
        page_info = {"count": count}
        page = int(request.args.get('page', 1))
        page_info["total"] = int(math.ceil(count / float(NUM_PER_PAGE)))
        if page > page_info["total"] or page < 1: page = 1
        page_info["page"] = page
        search_q_list = DB.search_q.find({"count": 0}).skip((page-1)*NUM_PER_PAGE).limit(NUM_PER_PAGE)
        return self._view.render('search_q_manage', search_q_list=list(search_q_list), page_info=page_info)

class DeleteView(View):
    @route('/delete', endpoint='admin_search_q_delete')
    def get(self):
        try:
            _id = request.args.get('_id')
            res = DB.search_q.remove({'_id': ObjectId(_id)})
            status, message = 'success', '删除成功'
        except Exception, ex:
            status, message = 'error', str(ex)
        return self._view.ajax_response(status, message)
