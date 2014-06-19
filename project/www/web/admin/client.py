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
    route_base = '/client-manager'
    def before_request(self, name):
        self._view = AdminView()

class ListView(View):
    @route('/list', endpoint='admin_client_list')
    def get(self):
        client_list = DB.client.find()
        client_type_list = DB.client_type.find()
        return self._view.render('client', client_list=list(client_list),
                                  client_type_list = list(client_type_list))

class AddView(View):
    @route('/add', methods=['POST'], endpoint='admin_client_add')
    def post(self):
        store_path = ""
        tp = DB.client_type.find({'type_id': request.form["type"]})
        last_version = DB.client.find_one({"type": tp[0]["type_id"]})
        if last_version:
            version = last_version["version"]
        else:
            version = ""
        if request.files["ipa"].filename != "":
            store_path, changed = upload_client_file(request.files["ipa"], tp[0]["ipaname"], 
                                            version, request.form['version'], request.form["review"],
                                            settings["client_upload_dir"])
            if changed and last_version:
                fileName, fileExtension = os.path.splitext(store_path)
                new_file_path = fileName + version + fileExtension
                DB.client.update({"_id": ObjectId(last_version["_id"])},
                                 {"$set": {"store_path": new_file_path}})
        try:
            data = {
                'version': request.form['version'],
                'review': request.form['review'],
                'build': request.form["build"],
                'type': tp[0]["type_id"],
                "store_path": store_path,
                'other_download': request.form["other_download"],
                'desc': request.form["desc"]
            }
            DB.client.insert(data)
            status, message = 'success', '添加成功'
        except Exception, ex:
            status, message = 'error', str(ex.message)
        return redirect(url_for("admin_client_list"))

class DeleteView(View):
    @route('/delete', endpoint='admin_client_delete')
    def get(self):
        try:
            _id = request.args.get('_id')
            res = DB.client.remove({'_id': ObjectId(_id)})
            status, message = 'success', '删除成功'
        except Exception, ex:
            status, message = 'error', str(ex)
        return self._view.ajax_response(status, message)

class ToggleStateView(View):
    @route('/toggle', endpoint='admin_client_toggle_state')
    def get(self):
        try:
            _id = request.args.get('_id')
            state = request.args.get("state")
            client_type = DB.client_type.find_one({"type_id" : request.args.get("type")})
            cli = DB.client.find_one({"_id": ObjectId(_id)})

            file_name, version = cli["store_path"], cli["version"]
            if state == "true":
                name, ext = os.path.splitext(file_name)
                new_name = name + "-%s" % version + ext
                state = "false"
                #rename the ipa
                DB.client.update({"_id": ObjectId(_id)}, {"$set": {"store_path": new_name}})
            else:
                state = "true"
                DB.client.update({"_id": ObjectId(_id)},
                    {"$set": {"store_path": os.path.join("/".join(settings["client_upload_dir"].split("/")[3:]), client_type["ipaname"])}})
            res = DB.client.update({"_id": ObjectId(_id)}, {"$set": {"review": state}})
            status, message = 'success', '更改成功'
        except Exception, ex:
            status, message = 'error', str(ex)
        return self._view.ajax_response(status, message)
