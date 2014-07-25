from __header__ import FlaskView, ApiView, route, request
from www.controller.app.other_ad import OtherAdController

class View(FlaskView):
    route_base = '/other_ad'

    def before_request(self, name):
        self._view = ApiView()


class InfoView(View):
    @route('/info', endpoint='api_other_ad_info')
    def get(self):
        device = request.args.get("device", "1")
        language = request.args.get("language", "en")
        jb = request.args.get("jb", "0")
        device_s = "iphone" if device == "1"  else "ipad"
        jb_s = "jb" if jb == "1" else "unjb"
        cs = device_s + jb_s
        other_add_controller = OtherAdController(language=language, ip=request.remote_addr, cs=cs)
        other_add = other_add_controller.get()
        return self._view.render(1000, list(other_add))
