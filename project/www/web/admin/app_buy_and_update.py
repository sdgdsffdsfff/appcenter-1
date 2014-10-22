#encoding=UTF8
import main, hashlib, math
from flask.ext.login import UserMixin
from __header__ import AdminView, FlaskView
from __header__ import DB, route
from flask.ext.login import current_user
from functools import wraps
from flask import request, abort
from bson.objectid import ObjectId
from datetime import datetime
from random import randint
from collections import defaultdict
import pytz

class View(FlaskView):
    route_base = '/app-buy-manager'
    def before_request(self, name):
        self._view = AdminView()

class ListView(View):
    @route('/list', endpoint='app_buy')
    def get(self):
        indicators = defaultdict(dict)
        editors = DB.User.find({'role': 'Editor'},{'_id': 0, 'username': 1})
        for editor in editors:
            indicators[editor['username']]['buy'] = DB.app_process_log.find({'status': 'finished', 'editor': editor['username'], 'buy_time': {'$exists': True}}).count()
            indicators[editor['username']]['update'] = DB.app_process_log.find({'status': 'finished', 'editor': editor['username'], 'update_time': {'$exists': True}}).count()

        page = int(request.args.get('page', 1))
        page_size = request.args.get('page_size', 10)
        res = DB.app_process.find({'apple_account': {'$exists': False},
                                   'status': {'$ne': 'finished'},
                                   'editor': current_user.username}). \
            sort('status').skip((page -1)*page_size).limit(page_size)
        total_page = int(math.ceil(res.count() / float(page_size)))
        offset = (page - 1) * page_size
        prev_page = (page - 1) if page - 1 > 0 else 1
        next_page = (page + 1) if page + 1 < total_page else total_page
        page_info = {"count": res.count(), "page": page, "total_page": total_page,
                     "prev_page": prev_page, 'next_page': next_page}
        to_buy_count = DB.app_process.find({'apple_account': {'$exists': False}, 'status': {'$ne': 'finished'}}).count()
        to_update_count = DB.app_process.find({'apple_account': {'$exists': True}, 'status': {'$ne': 'finished'}}).count()
        to_process_count = DB.app_process.find({'status': {'$ne': 'finished'}}).count()
        return self._view.render('app_buy_manage', results=res,
                                 to_buy_count=to_buy_count,
                                 to_update_count=to_update_count,
                                 to_process_count=to_process_count,
                                 page_info=page_info,
                                 indicators=indicators)

class UpdateListView(View):
    @route('/update_list', endpoint='app_update')
    def get(self):
        indicators = defaultdict(dict)
        editors = DB.User.find({'role': 'Editor'},{'_id': 0, 'username': 1})
        for editor in editors:
            indicators[editor['username']]['buy'] = DB.app_process_log.find({'status': 'finished', 'editor': editor['username'], 'buy_time': {'$exists': True}}).count()
            indicators[editor['username']]['update'] = DB.app_process_log.find({'status': 'finished', 'editor': editor['username'], 'update_time': {'$exists': True}}).count()

        page = int(request.args.get('page', 1))
        page_size = request.args.get('page_size', 10)
        res = DB.app_process.find({'apple_account': {'$exists': True},
                                   'status': {'$ne': 'finished'},
                                   'editor': current_user.username}). \
            sort('status').skip((page -1)*page_size).limit(page_size)
        total_page = int(math.ceil(res.count() / float(page_size)))
        offset = (page - 1) * page_size
        prev_page = (page - 1) if page - 1 > 0 else 1
        next_page = (page + 1) if page + 1 < total_page else total_page
        page_info = {"count": res.count(), "page": page, "total_page": total_page,
                     "prev_page": prev_page, 'next_page': next_page}
        return self._view.render('app_update_manage', results=res, page_info=page_info, indicators=indicators)

class AllListView(View):
    @route('/all_list', endpoint='app_all')
    def get(self):
        indicators = defaultdict(dict)
        editors = DB.User.find({'role': 'Editor'},{'_id': 0, 'username': 1})
        for editor in editors:
            indicators[editor['username']]['buy'] = DB.app_process_log.find({'status': 'finished', 'editor': editor['username'], 'buy_time': {'$exists': True}}).count()
            indicators[editor['username']]['update'] = DB.app_process_log.find({'status': 'finished', 'editor': editor['username'], 'update_time': {'$exists': True}}).count()

        page = int(request.args.get('page', 1))
        page_size = request.args.get('page_size', 10)
        res = DB.app_process_log.find({'editor': current_user.username}). \
            sort('status').skip((page -1)*page_size).limit(page_size)
        total_page = int(math.ceil(res.count() / float(page_size)))
        offset = (page - 1) * page_size
        prev_page = (page - 1) if page - 1 > 0 else 1
        next_page = (page + 1) if page + 1 < total_page else total_page
        page_info = {"count": res.count(), "page": page, "total_page": total_page,
                     "prev_page": prev_page, 'next_page': next_page}
        return self._view.render('app_all_manage', results=res, page_info=page_info, indicators=indicators)


class GetTaskView(View):
    @route('/get-task', endpoint='get_buy_task')
    def get(self):
        track_id = str(randint(100000000, 999999999))
        track_name = "Heads Up!"
        version = "2.3.5"
        price = 19
        currency = "USD"
        link_url = "https://itunes.apple.com/app/id623592465"
        new_app_task = {
            "track_id": track_id,
            "track_name": track_name,
            "new_version": version,
            "price": price,
            "link_url": link_url,
            "currency": currency,
            "status": "new",
            "editor": current_user.username,
            "recieve_time": datetime.now(pytz.timezone('Asia/Shanghai'))
        }
        DB.app_process.insert(new_app_task)
        new_app_task['recieve_time'] = new_app_task['recieve_time'].strftime('%Y-%m-%d')
        return self._view.ajax_response('success', new_app_task)


class BuyAppView(View):
    @route('/buy', methods=['POST'], endpoint='buy_app')
    def post(self):
        try:
            track_id = request.form.get('track_id', '')
            res = DB.app_process.update({'track_id': track_id},
                                        {'$set': {'status': 'processing'}})
            status, message = 'success', res
            data = DB.app_process.find_one({'track_id': track_id,
                                   'status': {'$ne': 'finished'}}, {'_id': 0})
            data['buy_time'] = datetime.now(pytz.timezone('Asia/Shanghai'))
            data['editor'] = current_user.username
            DB.app_process_log.insert(data)
        except Exception, ex:
            status, message = 'error', str(ex.message)

        return self._view.ajax_response(status, message)


class UpdateAppView(View):
    @route('/update', methods=['POST'], endpoint='update_app')
    def post(self):
        try:
            track_id = request.form.get('track_id', '')
            res = DB.app_process.update({'track_id': track_id},
                                        {'$set': {'status': 'processing'}})
            status, message = 'success', res
            data = DB.app_process.find_one({'track_id': track_id,
                                   'status': {'$ne': 'finished'}}, {'_id': 0})
            data['update_time'] = datetime.now(pytz.timezone('Asia/Shanghai'))
            data['editor'] = current_user.username
            DB.app_process_log.insert(data)
        except Exception, ex:
            status, message = 'error', str(ex.message)
        return self._view.ajax_response(status, message)
