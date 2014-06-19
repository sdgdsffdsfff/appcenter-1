#encoding=UTF8
#code by LP
#2013-11-7

from __header__ import AdminView, FlaskView, DB, route, request, session, redirect, url_for
import requests
import cjson
import urllib


class View(FlaskView):

    route_base = '/visual_editor'

    def before_request(self, name):
        self._view = AdminView()
        self._host = 'http://' + request.host

class IphoneSimulatorView(View):

    @route('/simulator', endpoint='admin_visual_editor_simulator')
    def get(self):
        l = request.args.get('l', 'ZH')
        c = request.args.get('c', 'ZH')
        langs = DB.client_support_language.find()
        countries = DB.country.find()
        self._view.assign('langs', list(langs))
        self._view.assign('countries', list(countries))
        self._view.assign('filter', {'lang': l, 'country': c})
        return self._view.render('visual_editor/iphone_simulator', title="可视化编辑器")


class IphoneEditorView(View):

    @route('/iphone_editor', endpoint='admin_visual_editor_iphone_editor')
    def get(self):
        self._view.assign('lang', request.args.get('lang', 'ZH'))
        self._view.assign('country', request.args.get('country', 'ZH'))
        return self._view.render('visual_editor/iphone_editor', title="可视化编辑器")


class IphoneHomeScreenView(View):

    @route('/iphone/home_screen', methods=['GET', 'POST'], endpoint='admin_visual_editor_iphone_home_screen')
    def do_request(self):
        if request.method != 'POST':
            return self._view.ajax_render('visual_editor/iphone_home_screen')

        l = request.args.get('lang', 'ZH')
        c = request.args.get('country', 'ZH')
        url = '%s%s' % (self._host, url_for('api_iphone_home_page', language=l, country=c))
        r = requests.get(url)
        return r.content


class IphoneTopicScreenView(View):

    @route('/iphone/topic_screen', methods=['GET', 'POST'], endpoint='admin_visual_editor_iphone_topic_screen')
    def do_request(self):
        if request.method != 'POST':
            return self._view.ajax_render('visual_editor/iphone_topic_screen')

        l = request.args.get('lang', 'ZH')
        c = request.args.get('country', 'ZH')
        url = '%s%s' % (self._host, url_for('api_app_topic_list', language=l, country=c))
        r = requests.get(url)
        return r.content
