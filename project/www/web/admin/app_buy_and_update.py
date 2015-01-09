#encoding=UTF8
import main, hashlib, math
from flask.ext.login import UserMixin
from __header__ import AdminView, FlaskView
from __header__ import DB, route, rsm
from flask.ext.login import current_user
from functools import wraps
from flask import request, abort, redirect, url_for
from bson.objectid import ObjectId
from datetime import datetime
from collections import defaultdict
import pytz
import json
import pymongo


class View(FlaskView):
    route_base = '/app-buy-manager'

    def before_request(self, name):
        self._view = AdminView()
        temp_indicators = defaultdict(dict)
        editors = DB.User.find({'role': 'Editor'}, {'_id': 0, 'username': 1})
        for editor in editors:
            temp_indicators[editor['username']]['buy'] = \
                DB.app_process_log.find(
                    {'status': 'bought', 'editor': editor['username']}).count()
            temp_indicators[editor['username']]['update'] = \
                DB.app_process_log.find(
                    {'status': 'updated',
                     'editor': editor['username']}).count()

        indicators = defaultdict(list)

        for i in range(len(temp_indicators)):
            indicators[i/3].append(temp_indicators.popitem())

        self._view.assign('indicators', indicators)

    def pagination(self, res, page, page_size):
        total_page = int(math.ceil(res.count() / float(page_size)))
        prev_page = (page - 1) if page - 1 > 0 else 1
        next_page = (page + 1) if page + 1 < total_page else total_page
        page_info = {"count": res.count(), "page": page,
                     "total_page": total_page, "prev_page": prev_page,
                     'next_page': next_page}
        self._view.assign('page_info', page_info)


class ListView(View):
    @route('/list', endpoint='app_buy')
    def get(self):
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))

        res = DB.app_process.find(
            {'$or': [{'status': 'buy'}, {'status': 'buying'}],
             'editor': current_user.username}).sort(
                 [('status', pymongo.ASCENDING),
                  ('recieve_time', pymongo.DESCENDING)]).skip(
                      (page - 1)*page_size).limit(page_size)

        self.pagination(res, page, page_size)

        to_buy_count = DB.app_process.find(
            {'$or': [{'status': 'buy'}, {'status': 'buying'}]}).count()
        to_update_count = DB.app_process.find(
            {'$or': [{'status': 'update'}, {'status': 'updating'}]}).count()
        to_process_count = to_buy_count + to_update_count

        return self._view.render('app_buy_manage', results=res,
                                 to_buy_count=to_buy_count,
                                 to_update_count=to_update_count,
                                 to_process_count=to_process_count)


class UpdateListView(View):
    @route('/update_list', endpoint='app_update')
    def get(self):
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))

        res = DB.app_process.find(
            {'$or': [{'status': 'update'}, {'status': 'updating'}],
             'editor': current_user.username}).sort(
                 [('status', pymongo.ASCENDING),('apple_account', pymongo.ASCENDING)]).skip(
                     (page - 1)*page_size).limit(page_size)

        self.pagination(res, page, page_size)
        return self._view.render('app_update_manage', results=res)


class AllListView(View):
    @route('/all_list', endpoint='app_all')
    def get(self):

        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))

        res = DB.app_process_log.find(
            {'editor': current_user.username}).sort(
                [('status', pymongo.ASCENDING),
                 ('buy_time', pymongo.DESCENDING)]).skip(
                     (page - 1) * page_size).limit(page_size)

        self.pagination(res, page, page_size)

        return self._view.render('app_all_manage', results=res)


class GetTaskView(View):
    @route('/get-task', endpoint='get_buy_task')
    def get(self):
        while True:
            #data = json.loads(rsm.rpop('app_process'))
            value = rsm.rpop('app_process_first')
            data = json.loads(value) if value else json.loads(rsm.rpop('app_process'))
            if not DB.app_process.find_one({'track_id': data['track_id']}):
                break
        country = None
        if 'CN' in data['info']:
            q_res = data['info']['CN']
            country = 'CN'
            DB.AppBase_CN.update({"trackId": data['track_id']}, {"$set": q_res}, True)
            if 'US' not in data['info']: DB.AppBase.update({"trackId": data['track_id']}, {"$set": q_res}, True)
        if 'US' in data['info']:
            q_res = data['info']['US']
            country = 'US'
            DB.AppBase.update({"trackId": data['track_id']}, {"$set": q_res}, True)
        if 'SA' in data['info']:
            q_res = data['info']['SA']
            country = 'SA'
            DB.AppBase.update({"trackId": data['track_id']}, {"$set": q_res}, True)
        if country is None:
            country = data['info'].keys()[0]
            q_res = data['info'][country]
            DB.AppBase.update({"trackId": data['track_id']}, {"$set": q_res}, True)

        # link_url = "https://itunes.apple.com/app/id%s" % str(data['track_id'])
        link_url = q_res.get("trackViewUrl", "")
        new_app_task = {
            "track_id": data['track_id'],
            "track_name": q_res['trackName'],
            "new_version": q_res['version'],
            "price": q_res['price'],
            "link_url": link_url,
            "currency": q_res['currency'],
            "country": country,
            "status": "buy",
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
            track_id = int(request.form.get('track_id', 0))
            res = DB.app_process.update(
                {'track_id': track_id}, {'$set': {'status': 'buying'}})
            status, message = 'success', res
            data = DB.app_process.find_one({'track_id': track_id}, {'_id': 0})
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
            track_id = int(request.form.get('track_id', 0))
            res = DB.app_process.update({'track_id': track_id},
                                        {'$set': {'status': 'updating'}})
            status, message = 'success', res
            data = DB.app_process.find_one({'track_id': track_id}, {'_id': 0})
            data['update_time'] = datetime.now(pytz.timezone('Asia/Shanghai'))
            data['editor'] = current_user.username
            DB.app_process_log.insert(data)
        except Exception, ex:
            status, message = 'error', str(ex.message)
        return self._view.ajax_response(status, message)

class DeleteAppView(View):
    @route('/delete', methods=['POST'], endpoint='delete_app')
    def post(self):
        try:
            track_id = int(request.args.get('track_id', 0))
            DB.app_process.remove({'track_id': track_id})
            status, message = 'success', ''
            return redirect(url_for('app_buy'))
        except Exception, ex:
            status, message = 'error', str(ex.message)
            return message
