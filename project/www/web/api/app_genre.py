#encoding=UTF-8
#code by LP
#2013-11-4
import main
from __header__ import FlaskView, ApiView, route, request
from www.controller.app.app_genre import AppGenreController
from conf.settings import CACHE_TIME

class View(FlaskView):
    route_base = '/app_genre'
    def before_request(self, name):
        self._view = ApiView()


class ListView(View):
    @route('/list', endpoint='api_app_genre_list')
    @main.cache.cached(timeout=CACHE_TIME * 6)
    def get(self):
        genre_id = request.args.get('parent_genre', 0)
        genre = AppGenreController(self._view._language)
        data = genre.get_list(int(genre_id))
        return self._view.render(1000, data)
