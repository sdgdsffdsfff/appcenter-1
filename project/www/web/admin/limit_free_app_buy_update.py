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
    route_base = '/limit-app-feee-buy-update'

    def before_request(self, name):
        self._view = AdminView()
        temp_indicators = defaultdict(dict)
        editors = DB.User.find({'role': 'Editor'}, {'_id': 0, 'username': 1})
        for editor in editors:
            temp_indicators[editor['username']]['buy'] = \
                DB.limit_app_process_log.find(
                    {'status': 'bought', 'editor': editor['username']}).count()
            temp_indicators[editor['username']]['update'] = \
                DB.limit_app_process_log.find(
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


class LimitFreeListView(View):
    @route('/list', endpoint='limit_app_buy')
    def get(self):
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))

        res = DB.limit_app_process.find(
            {'$or': [{'status': 'buy'}, {'status': 'buying'}],
             'editor': current_user.username}).sort(
                 [('status', pymongo.ASCENDING),
                  ('recieve_time', pymongo.DESCENDING)]).skip(
                      abs((page - 1))*page_size).limit(page_size)

        self.pagination(res, page, page_size)

        to_buy_count = DB.limit_app_process.find(
            {'$or': [{'status': 'buy'}, {'status': 'buying'}]}).count()
        to_update_count = DB.limit_app_process.find(
            {'$or': [{'status': 'update'}, {'status': 'updating'}]}).count()
        to_process_count = to_buy_count + to_update_count

        not_receive_count = DB.limit_free_app.find().count()

        return self._view.render('limit_free_app_buy_manage', results=res,
                                 to_buy_count=to_buy_count,
                                 to_update_count=to_update_count,
                                 to_process_count=to_process_count,
                                 not_receive_count = not_receive_count)

class LimitFreeGetTaskView(View):
    @route('/get-task', endpoint='limit_free_get_buy_task')
    def get(self):

        s_res = DB.limit_free_app.find()
        if s_res.count() != 0:
            new_app_task = {}
            for item in s_res:
                d_res = DB.limit_app_process.find_one({"track_id":item["track_id"]})
                if not d_res:
                    res = DB.limit_free_app.find_one({"track_id":item["track_id"],"country":{"$in":["US","SA"]}})
                    if res:
                        new_app_task = self.get_new_task(res)
                    else:
                        new_app_task = self.get_new_task(DB.limit_free_app.find_one({"track_id":item["track_id"]}))

                    DB.limit_app_process.insert(new_app_task)
                    DB.limit_free_app.remove({"track_id":item["track_id"]})
                    new_app_task['recieve_time'] = new_app_task['recieve_time'].strftime('%Y-%m-%d')
                    return self._view.ajax_response('success', new_app_task)
                elif d_res:
                    DB.limit_free_app.remove({"track_id":item["track_id"]})
                    #防止点击领取任务时，如果limit_free_app数据库中如果有和limit_app_process重复的数据而引起的点击没有反应
                    if DB.limit_free_app.find().count():
                        continue
                    else:
                        message = str('The current has no free app for buy')
                        return self._view.ajax_response('failed',message)

                else:
                    continue
        else:
            message = str('The current has no free app for buy')
            return self._view.ajax_response('failed',message)

    def get_new_task(self,item):
        new_app_task = {
                        "track_id": item['track_id'],
                        "track_name": item['info']['trackName'],
                        "local_version": item['version'],
                        "new_version":item['version'],
                        "price": item['price'],
                        "link_url": item['info']['trackViewUrl'],
                        "currency": item['info']['currency'],
                        "country": item["country"],
                        "status": "buy",
                        "editor": current_user.username,
                        "recieve_time": datetime.now(pytz.timezone('Asia/Shanghai'))
                    }
        return new_app_task


class LimitFreeDeleteAppView(View):
    @route('/delete', methods=['POST'], endpoint='limit_free_delete_app')
    def post(self):
        try:
            track_id = int(request.args.get('track_id', 0))
            country = request.args.get('country','')

            DB.limit_app_process.remove({'track_id': track_id,'country':country})
            status, message = 'success', ''
            return redirect(url_for('limit_app_buy'))
        except Exception, ex:
            status, message = 'error', str(ex.message)
            return message


class LimitFreeBuyAppView(View):
    @route('/buy', methods=['POST'], endpoint='limit_buy_app')
    def post(self):
        try:
            track_id = int(request.form.get('track_id', 0))
            country = request.form.get('country',' ')

            res = DB.limit_app_process.update(
                {'track_id': track_id,'country':country}, {'$set': {'status': 'buying'}})
            status, message = 'success', res

            data = DB.limit_app_process.find_one({'track_id': track_id,'country':country}, {'_id': 0})
            data['buy_time'] = datetime.now(pytz.timezone('Asia/Shanghai'))
            data['editor'] = current_user.username
            DB.limit_app_process_log.insert(data)


            # data = DB.app_process.find_one({'track_id': track_id}, {'_id': 0})
            # data['buy_time'] = datetime.now(pytz.timezone('Asia/Shanghai'))
            # data['editor'] = current_user.username
            # DB.app_process_log.insert(data)
        except Exception, ex:
            status, message = 'error', str(ex.message)

        return self._view.ajax_response(status, message)


class LimitUpdateListView(View):
    @route('/update_list', endpoint='limit_app_update_list')
    def get(self):
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))

        res = DB.limit_app_process.find(
            {'$or': [{'status': 'update'}, {'status': 'updating'}],
             'editor': current_user.username}).sort(
                 'status', pymongo.ASCENDING).skip(
                     (page - 1)*page_size).limit(page_size)

        self.pagination(res, page, page_size)
        return self._view.render('limit_free_app_update', results=res)

class LimitUpdateAppView(View):
    @route('/update', methods=['POST'], endpoint='limit_update_app')
    def post(self):
        try:
            track_id = int(request.form.get('track_id', 0))
            country = request.form.get('country','')
            res = DB.limit_app_process.update({'track_id': track_id,'country':country},
                                        {'$set': {'status': 'updating'}})
            status, message = 'success', res
            data = DB.limit_app_process.find_one({'track_id': track_id,'country':country}, {'_id': 0})
            data['update_time'] = datetime.now(pytz.timezone('Asia/Shanghai'))
            data['editor'] = current_user.username
            DB.limit_app_process_log.insert(data)   #may be need changed
        except Exception, ex:
            status, message = 'error', str(ex.message)
        return self._view.ajax_response(status, message)

class LimitAllListView(View):
    @route('/all_list', endpoint='limit_app_all_list')
    def get(self):

        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))

        res = DB.limit_app_process_log.find(
            {'editor': current_user.username}).sort(
                [('status', pymongo.ASCENDING),
                 ('buy_time', pymongo.DESCENDING)]).skip(
                     (page - 1) * page_size).limit(page_size)

        self.pagination(res, page, page_size)

        return self._view.render('limit_app_all_manage', results=res)