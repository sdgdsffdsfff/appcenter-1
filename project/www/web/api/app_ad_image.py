#encoding=UTF-8
#code by LP
#2013-11-4

from __header__ import FlaskView, ApiView, route, request
from www.controller.app.app_ad_image import AppAdImageController

class View(FlaskView):

    route_base = '/app_ad_image'

    def before_request(self, name):
        self._view = ApiView()


class ListView(View):
    @route('/list', endpoint='api_ad_image_list')
    def get(self):
        app_add_images = AppAdImageController().get()
        return self._view.render(1000, app_add_images)
