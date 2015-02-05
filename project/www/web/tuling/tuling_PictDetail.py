#encoding=UTF-8
#code by LP
#2013-12-5

from __header__ import FlaskView, ApiView, route, request
from www.controller.tuling.tuling_PictDetail import AppTopicController

class View(FlaskView):

    route_base = '/picture'
    def before_request(self, name):
        self._view = ApiView()
        self.app_tuling = AppTopicController(self._view._language, self._view._ip)

class ListView(View):

    @route('/category', endpoint='tuling_PicDetail_list')
    def get(self):

        page= 1
        try:
            page = int(request.args.get('page', 1))
        except:
             pass
        if page < 1:
            page = 1

        obj_id = ''
        try:
            obj_id = request.args.get('id', '')
        except:
            pass
        type = ''
        try:
            type = request.args.get('type', '')
        except:
            pass
	sexi = ''
	try:
	    sexi = request.args.get('sexi','')

	except:
	    pass
        res = self.app_tuling.get_list(obj_id,page,type,sexi)

        return self._view.render(1000, res)
