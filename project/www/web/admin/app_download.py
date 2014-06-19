#encoding=UTF8
#code by LP
#2013-11-21

import os
import time
import random
from __header__ import AdminView, FlaskView, DB, route, request, session, redirect, url_for
from bson.objectid import ObjectId
from www.controller.app.app import AppController
from www.controller.app.app_download import AppDownloadController

class View(FlaskView):

    route_base = '/app_download'

    def before_request(self, name):
        self._view = AdminView()
        self.app_download = AppDownloadController()
        self.app = AppController()

class ListView(View):
    '''
    下载
    '''
    @route('/list', endpoint='admin_app_download_list')
    def get(self):
        bundle_id = request.args.get('bundleId', None)
        if bundle_id is None:
            return self._view.error("参数错误")

        app = self.app.get_by_bundleid(bundle_id)
        download_list = self.app_download.get_by_bundleid(bundle_id)

        return self._view.render('app_download', download_list=download_list, app=app)


class DeleteView(View):

    @route('/delete', endpoint='admin_app_download_delete')
    def do_request(self):
        _id = request.args.get('_id', None)
        if _id is None:
            status, message = 'error', '参数错误'
            return self._view.ajax_response(status, message)
        try:
            self.app_download.delete_by_objectid(_id)
            status, message = 'success', '删除成功'
        except Exception, ex:
            status, message = 'error', str(ex)
        return self._view.ajax_response(status, message)

class UploadView(View):

    def allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1] == 'ipa'

    @route('/upload', methods=['POST'], endpoint='admin_app_download_upload')
    def do_request(self):
        try:
            bundle_id = request.form['bundleId']
            sign = 0
        except:
            return self._view.ajax_response('error', u'参数错误')

        try:
            file = request.files['Filedata']
            if file and self.allowed_file(file.filename):
                name = str(time.time()) + '_' + file.filename
                tmp_file = os.path.join(vshare_settings['tmp_dir'], name)
                file.save(tmp_file)
                self.app_download.add(bundle_id=bundle_id, sign=sign, file_path=tmp_file)
                status, message = 'success', u'上传成功'
            else:
                raise Exception(u'必须是IPA文件')
        except Exception, ex:
            status, message = 'error', u'上传失败:' + str(ex)
        return self._view.ajax_response(status, message)
