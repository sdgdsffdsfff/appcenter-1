#encoding=UTF-8
#code by LP
#2014-06-17


from __header__ import FlaskView, ApiView, route, request
from www.controller.client import ClientController
from flask import make_response

class View(FlaskView):

    route_base = '/client'
    
    def before_request(self, name):
        self._view = ApiView()

class UpdateView(View):
    """
    ios client update
    """
    @route('/ios/update', endpoint='api_client_ios_update')
    def get(self):
    	"""
    	client type (jb,signed,cydia,jb_facebook, signed_facebook, jb_media, signed_media)
    	"""
    	client_type = request.args.get('type', 'jb')
        language = request.args.get('language', 'zh-Hans')
        if language == "cn": language = 'zh-Hans'
        client = ClientController()
        data = client.get_latest_version(client_type, language=language)
        return self._view.render(1000, data)

class PlistView(View):
    """
    ios client update
    """
    @route('/ios/plist', endpoint='api_client_ios_plist')
    def get(self):
        client_type = request.args.get('type', 'jb')
        client = ClientController()
        plist = client.get_latest_version_plist(client_type)
        resp = make_response(plist, 200)
        resp.headers['Content-Type'] = 'application/xml'
        return resp
