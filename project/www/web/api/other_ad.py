from __header__ import FlaskView, ApiView, route, request
from www.controller.app.other_ad import OtherAdController

class View(FlaskView):

    route_base = '/other_ad'

    def before_request(self, name):
        self._view = ApiView()


class InfoView(View):
    @route('/info', endpoint='api_other_ad_info')
    def get(self):
        other_add_controller = OtherAdController()
        other_add = other_add_controller.get()
        return self._view.render(1000, other_add)
