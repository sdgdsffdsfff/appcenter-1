#encoding=UTF-8
#code by LP
#2013-11-4
import main
from __header__ import FlaskView, ApiView, route, request
from www.controller.app.app import AppController
from www.controller.app.search import AppSearch
from conf.settings import CACHE_TIME

class View(FlaskView):

    route_base = '/app'

    def before_request(self, name):
        self._view = ApiView()
        self.app = AppController(language=self._view._language)


class DetailView(View):
    '''
    获取应用详细
    '''
    @route('/detail', endpoint='api_app_detail')
    @main.cache.cached(timeout=CACHE_TIME)
    def get(self):
        data = {}
        object_id = request.args.get('id', None)
        if object_id is not None:
            try: data = self.app.get_app_detail(object_id, self._view.vv_version)
            except Exception, ex: pass
        return self._view.render(1000, data)


class ListView(View):
    """
    获取应用列表
    """
    @route('/list', endpoint='api_app_list')
    #@main.cache.cached(timeout=CACHE_TIME)
    def get(self):
        genre_id = request.args.get('genre_id', 0)
        device = request.args.get('device', "1")
        sort = request.args.get('sort', 'sort')
        page = request.args.get('page', 1)
        '''
        xsort = 'sort'
        if sort == 'new': xsort = '_id'
        elif sort == 'hot': xsort = 'downloadCount'
        '''
        # 手机api 热门与最新 对应所传过来的值颠倒了
        if sort =='hot':
            sort ='new'
        elif sort =='new':
            sort ='hot'
        if device == 'ipad' or device == "2": device = 'ipad'
        else: device = 'iphone'
        #data = self.app.get_apps_cache(device, self._view._sign, genre_id, int(page), xsort)
        data = self.app.get_apps_cache_mg(device, self._view._sign, genre_id, int(page), sort)
        return self._view.render(1000, data)


class CheckUpdateView(View):
    """
    检查更新
    """
    @route('/check_update', methods=['GET','POST'], endpoint='api_app_check_update')
    def do_request(self):
        local_packages = {}
        try:
            bundle_id = request.form['bid']
        except:
            bundle_id = request.args.get('bid', None)
        if bundle_id is None: return self._view.render(2000)
        bundle_ids = bundle_id.split(',')
        for row in bundle_ids:
            try:
                bundle_id, version = row.split('|')
                local_packages[bundle_id] = version
            except:
                continue
        results = self.app.check_update_by_all(local_packages, self._view._sign)
        return self._view.render(1000, results)

class RelatedView(View):
    """
    相关的应用
    """
    @route('/related', methods=['GET'], endpoint='api_app_related')
    @main.cache.cached(timeout=CACHE_TIME)
    def do_request(self):
        object_id = request.args.get('id', None)
        num = request.args.get('num', 4)
        apps = self.app.get_related_app(object_id, self._view._language, int(num))
        return self._view.render(1000, apps)

class SearchView(View):
    """
    搜索
    """
    @route('/search', methods=['GET'], endpoint='api_app_search')
    @main.cache.cached(timeout=CACHE_TIME)
    def do_request(self):
        words = request.args.get('q', None)
        try:
            page = int(request.args.get('page', 1))
        except:
            page = 1
        try:
            device = int(request.args.get('device', 1))
        except:
            device = 1
        num = request.args.get('num', 4)
        search = AppSearch()
        res = search.query(words, device, self._view._sign, page, 12, self._view._language)
        return self._view.render(1000, res)
