#!/usr/bin/env python
# encoding: utf-8


from www.controller.app.app_process import AppProcess
from __header__ import FlaskView, ApiView, route, request


class View(FlaskView):
    route_base = '/app_process'

    def before_request(self, name):
        self._view = ApiView()

#/api/app_process/finish
class FinishView(View):
    @route('/finish', methods=['POST'], endpoint='api_app_process_finish')
    #@route('/finish', methods=['GET','POST'], endpoint='api_app_process_finish')
    def post(self):
        app_process = AppProcess()
        try:
            track_id = int(request.form.get('trackid', 0))
            bundle_version = request.form.get('bundle_version', '')
            apple_account = request.form.get('apple_account', '')
            #track_id = int(request.args.get('track_id', ''))
            #bundle_version = request.args.get('bundle_version', '')
            #apple_account = request.args.get('apple_account', '')

            result = app_process.finish_process(track_id, bundle_version,
                                                apple_account)
        except:
            result = 2000
        return self._view.render(result, '')
