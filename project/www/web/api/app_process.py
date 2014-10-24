#!/usr/bin/env python
# encoding: utf-8


from www.controller.app.app_process import AppProcess
from __header__ import FlaskView, ApiView, route, request


class View(FlaskView):
    route_base = '/app_process'
    def before_request(self, name):
        self._view = ApiView()


class BuyView(View):
    @route('/buy', methods=['POST'], endpoint='api_app_process_buy')
    def post(self):
        app_process = AppProcess()
        try:
            track_id = request.form.get('track_id', '')
            bundle_version = request.form.get('bundle_version', '')
            apple_account = request.form.get('apple_account', '')

            result1 = app_process.finish_process(track_id,
                                                 bundle_version,
                                                 apple_account)
            result2 = app_process.do_log('buy', track_id,
                                         bundle_version, apple_account)
            if result1 == 0 or result2 == 0:
                status = 2000
                message = 'something wrong happend while write to db'
            else:
                status, message = 1000, 'done'
        except Exception, ex:
            status, message = 2000, str(ex.message)
        return self._view.render(status, message)


class UpdateView(View):
    @route('/update', methods=['POST'], endpoint='api_app_process_update')
    def post(self):
        app_process = AppProcess()
        try:
            track_id = request.form.get('track_id', '')
            bundle_version = request.form.get('bundle_version', '')
            apple_account = request.form.get('apple_account', '')
            result1 = app_process.finish_process(track_id,
                                                 bundle_version,
                                                 apple_account)
            result2 = app_process.do_log('update', track_id,
                                         bundle_version, apple_account)
            if result1 == 0 or result2 == 0:
                status = 2000
                message = 'something wrong happend while write to db'
            else:
                status, message = 1000, 'done'
        except Exception, ex:
            status, message = 2000, str(ex.message)
        return self._view.render(status, message)
