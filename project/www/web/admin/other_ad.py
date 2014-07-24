#encoding=UTF8
import main, hashlib
from flask.ext.login import UserMixin
from __header__ import AdminView, FlaskView
from __header__ import DB, route, upload_hash_file
from flask.ext.login import current_user
from functools import wraps
from flask import request, abort, redirect, url_for
from bson.objectid import ObjectId
from conf.settings import settings

class View(FlaskView):
    route_base = '/other-ad-manager'
    def before_request(self, name):
        self._view = AdminView()

class ListView(View):
    @route('/list', endpoint='admin_other_ad_list')
    def get(self):
        other_ad_list = DB.other_ad.find()
        languages = DB.language.find({}, {"_id": 0})
        locations = DB.location.find({}, {"_id": 0})
        return self._view.render('other_ad_manage',
                                 other_ad_list=list(other_ad_list),
                                 languages=list(languages),
                                 locations=list(locations))

class EditView(View):
    @route('/edit', methods=['POST'], endpoint='admin_other_ad_edit')
    def post(self):
        try:
            data = {
                "cses" : request.form.getlist("cses"),
                "languages": request.form.getlist("languages"),
                "locations": request.form.getlist("locations"),
                "status": int(request.form.get("status", 0)),
                "source": request.form["source"],
                "child_positions": request.form.getlist("child_positions")
            }
            DB.other_ad.update({"position": request.form['position']}, {"$set": data}, True)
            status, message = 'success', '添加成功'
        except Exception, ex:
            status, message = 'error', str(ex.message)
        return self._view.ajax_response(status, message)

class CustomAdListView(View):
    @route('/customad-list', endpoint='admin_other_ad_customad_list')
    def get(self):
        position = request.args.get("position")
        other_ad = DB.other_ad.find_one({"position": position})
        customad_list = other_ad.get("data", [])
        languages = DB.language.find({}, {"_id": 0})
        locations = DB.location.find({}, {"_id": 0})
        return self._view.render('other_ad_customad_manage',
                                 other_ad = other_ad,
                                 other_ad_customad_list=list(customad_list),
                                 languages=list(languages),
                                 locations=list(locations))

class CustomadDeleteView(View):
    @route('/customad-delete', endpoint='admin_customad_delete')
    def get(self):
        try:
            hash_str = request.args.get("hash")
            position = request.args.get("position")
            DB.other_ad.update({"position": position}, {"$pull": { "data": {
                "hash": hash_str
            }}})
            status, message = 'success', '删除成功'
        except Exception, ex:
            status, message = 'error', str(ex)
        return self._view.ajax_response(status, message)

class CustomadAddView(View):
    @route('/customad-add', methods=["POST"], endpoint='admin_customad_add')
    def post(self):
        try:
            position = request.form["position"]
            name = request.form["name"]
            link = request.form["link_url"]
            locations = request.form.getlist("locations")
            hash_str, abs_save_file, save_file = upload_hash_file(
                request.files["image_url"],
                settings["pic_upload_dir"]
            )
            DB.other_ad.update({"position": position}, {"$push": {"data": {
                "url": save_file,
                "link_url": link,
                "name": name,
                "hash": hash_str,
                "locations": locations
            }}})
        except Exception, ex:
            status, message = 'error', str(ex)
            print message
        return redirect(url_for("admin_other_ad_customad_list", position=position))
