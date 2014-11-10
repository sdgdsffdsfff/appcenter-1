#encoding=UTF8
import os
import hashlib
from functools import wraps

from flask.ext.login import UserMixin
from flask.ext.login import current_user
from flask import request, abort
from bson.objectid import ObjectId

import main
from conf.settings import settings
from __header__ import AdminView, FlaskView
from __header__ import (DB, route, upload_hash_file, url_for,
                        redirect, upload_client_file)


class View(FlaskView):
    route_base = '/notification'
    def before_request(self, name):
        self._view = AdminView()

class ListView(View):
    @route('/list', endpoint='admin_notification_list')
    def get(self):
        notifications = DB.notification.find()
        noti_list = notifications[0]["noti"]
        return self._view.render('notification', notifications=list(notifications), noti_list=noti_list)


class EditView(View):
    '''edit push notification content'''
    @route('/edit', methods=['POST'], endpoint='admin_notification_edit')
    def post(self):
        try:
            _id, pid = request.form['_id'], request.form["pid"]
            content = request.form["content"]
            DB.notification.update({"_id": ObjectId(_id), "noti.id": int(pid)}, {"$set": {"noti.$.content": content}})
            status, message = 'success', '更改成功'
        except Exception as ex:
            status, message = 'error', str(ex)
        return self._view.ajax_response(status, message)


class ToggleStateView(View):
    @route('/toggle', endpoint='admin_notification_toggle_state')
    def get(self):
        try:
            _id = request.args.get('_id')
            state = request.args.get("state")
            noti = DB.notification.find_one({"_id": ObjectId(_id)})
            if state == "True":
                DB.notification.update({"_id": ObjectId(_id)}, {"$set": {"published": False}})
            else:
                DB.notification.update({"_id": ObjectId(_id)},
                    {"$set": {"published": True}})
            status, message = 'success', '更改成功'
        except Exception, ex:
            status, message = 'error', str(ex)
        return self._view.ajax_response(status, message)
