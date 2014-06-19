#encoding=UTF-8
#code by LP
#2013-11-4

from header import *

from controller.app.app import AppController
from controller.app.app_genre import AppGenreController
from controller.app.search import AppSearch

class Base(WebSiteBase):

    def before(self):
        super(Base, self).before()
        self.app = AppController(language=self._language)


class RequestByBundleid(Base):
    '''
    通过bundleid获取应用
    '''

    def GET(self):
        data = {}
        bundleid = self.args['bundleid']
        data = self.app.get_app_cache(bundleid, False)
        self.assign('data', data)
        return self.render('detail')


class RequestList(Base):
    '''
    获取应用列表
    '''

    def GET(self):
        genre_id = request.args.get('genre_id', 0)
        device = request.args.get('device', 'iphone')
        sort = request.args.get('sort', 'sort')
        page = request.args.get('page', 1)

        xsort = 'sort'
        if sort == 'new':
            xsort = '_id'
        elif sort == 'down':
            xsort = 'downloadCount'

        data = self.app.get_apps_cache(device, genre_id, int(page), xsort)
        data['genre_id'] = genre_id
        data['device'] = device
        data['sort'] = sort
        genre = AppGenreController(self._language)
        data['genre'] = genre.get_list(36)

        self.assign('data', data)
        return self.render('list')


class Search(Base):
    """
    应用搜索
    """
    def GET(self):
        q = request.args.get('q', '')
        device = request.args.get('device', 'iphone')
        if device not in ['iphone', 'ipad']:
            device = 'iphone'
        try:
            page = int(request.args.get('page', 1))
        except:
            page = 1
        search = AppSearch()
        data = search.query(words=q, device=device, page=page, page_size=12)
        data['device'] = device
        data['q'] = q
        self.assign('data', data)
        return self.render('search')
