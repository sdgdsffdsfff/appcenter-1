#encoding=UTF-8
#code by LP
#2014-4-9

from flask import Flask, url_for
from flask.ext.login import LoginManager
from jinja2 import Environment
from flask.ext.cache import Cache
from conf.settings import settings

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

app = Flask(__name__, template_folder='www/templates', static_folder='www/static')
app.debug = False
app.secret_key = 'a2V*js%W$xd89saye3qhn&A32lk@'
login_manager = LoginManager()
login_manager.init_app(app)

MASTER_REDIS_CONF = settings['new_app_redis']['redis_master']

cache = Cache(app, config = {
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_HOST': MASTER_REDIS_CONF['host'],
    'CACHE_REDIS_PORT': MASTER_REDIS_CONF['port'],
    'CACHE_REDIS_PASSWORD': MASTER_REDIS_CONF['password']
})
cache.init_app(app)

login_manager.login_view = "/admin/login/"

app.jinja_options['extensions'].append('jinja2.ext.loopcontrols')

def register_view():
    import www.web.admin as admin
    import www.web.api as api
    admin.account.LoginView.register(app, route_prefix='/admin/')
    admin.account.LogoutView.register(app, route_prefix='/admin/')
    admin.index.DashboardView.register(app, route_prefix='/admin/')
    admin.visual_editor.IphoneSimulatorView.register(app, route_prefix='/admin/')
    admin.visual_editor.IphoneEditorView.register(app, route_prefix='/admin/')
    admin.visual_editor.IphoneHomeScreenView.register(app, route_prefix='/admin/')
    admin.visual_editor.IphoneTopicScreenView.register(app, route_prefix='/admin/')
    admin.app_genre.ListView.register(app, route_prefix='/admin/')
    admin.app_genre.SyncView.register(app, route_prefix='/admin/')
    admin.advertising.ListView.register(app, route_prefix='/admin/')
    admin.advertising.AddView.register(app, route_prefix='/admin/')
    admin.advertising.DeleteView.register(app, route_prefix='/admin/')
    admin.advertising.ItemListView.register(app, route_prefix='/admin/')
    admin.advertising.ItemAddView.register(app, route_prefix='/admin/')
    admin.advertising.ItemDeleteView.register(app, route_prefix='/admin/')
    admin.advertising.AdOrderUpdateView.register(app, route_prefix='/admin/')
    admin.advertising.ItemSearchView.register(app, route_prefix='/admin/')
    admin.app.ListView.register(app, route_prefix='/admin/')
    admin.app.CreateView.register(app, route_prefix='/admin/')
    admin.app.AddView.register(app, route_prefix='/admin/')
    admin.app.EditView.register(app, route_prefix='/admin/')
    admin.app.SortView.register(app, route_prefix='/admin/')
    admin.app.SyncIconView.register(app, route_prefix='/admin/')
    admin.app.SyncInfoView.register(app, route_prefix='/admin/')
    admin.app.ScreenshotView.register(app, route_prefix='/admin/')
    admin.app_download.ListView.register(app, route_prefix='/admin/')
    admin.app_download.DeleteView.register(app, route_prefix='/admin/')
    admin.app_download.UploadView.register(app, route_prefix='/admin/')
    admin.app_download.DownloadView.register(app, route_prefix='/admin/')
    admin.app_collection.ListView.register(app, route_prefix='/admin/')
    admin.app_collection.AddView.register(app, route_prefix='/admin/')
    admin.app_collection.DeleteView.register(app, route_prefix='/admin/')
    admin.app_collection.ItemListView.register(app, route_prefix='/admin/')
    admin.app_collection.ItemAddView.register(app, route_prefix='/admin/')
    admin.app_collection.ItemDeleteView.register(app, route_prefix='/admin/')
    admin.app_collection.ItemSortView.register(app, route_prefix='/admin/')
    admin.app_topic.ListView.register(app, route_prefix='/admin/')
    admin.app_topic.AddView.register(app, route_prefix='/admin/')
    admin.app_topic.EditView.register(app, route_prefix='/admin/')
    admin.app_topic.DeleteView.register(app, route_prefix='/admin/')
    admin.app_topic.ItemListView.register(app, route_prefix='/admin/')
    admin.app_topic.ItemAddView.register(app, route_prefix='/admin/')
    admin.app_topic.ItemDeleteView.register(app, route_prefix='/admin/')
    admin.app_topic.ItemSortView.register(app, route_prefix='/admin/')
    admin.app_topic.AppTopicOrderUpdateView.register(app, route_prefix='/admin/')
    admin.cache.InfoView.register(app, route_prefix='/admin/')
    admin.users.ListView.register(app, route_prefix='/admin/')
    admin.users.AddView.register(app, route_prefix='/admin/')
    admin.users.DeleteView.register(app, route_prefix='/admin/')
    admin.language.ListView.register(app, route_prefix='/admin/')
    admin.language.AddView.register(app, route_prefix='/admin/')
    admin.language.DeleteView.register(app, route_prefix='/admin/')
    admin.country.ListView.register(app, route_prefix='/admin/')
    admin.country.AddView.register(app, route_prefix='/admin/')
    admin.country.DeleteView.register(app, route_prefix='/admin/')
    admin.dirty_word.ListView.register(app, route_prefix='/admin/')
    admin.dirty_word.AddView.register(app, route_prefix='/admin/')
    admin.dirty_word.DeleteView.register(app, route_prefix='/admin/')
    admin.client_type.ListView.register(app, route_prefix='/admin/')
    admin.client_type.AddView.register(app, route_prefix='/admin/')
    admin.client_type.DeleteView.register(app, route_prefix='/admin/')
    admin.client.ListView.register(app, route_prefix='/admin/')
    admin.client.AddView.register(app, route_prefix='/admin/')
    admin.client.DeleteView.register(app, route_prefix='/admin/')
    admin.client.ToggleStateView.register(app, route_prefix='/admin/')
    admin.search_q.ListView.register(app, route_prefix='/admin/')
    admin.search_q.DeleteView.register(app, route_prefix='/admin/')
    admin.hotword.ListView.register(app, route_prefix='/admin/')
    admin.hotword.AddView.register(app, route_prefix='/admin/')
    admin.hotword.DeleteView.register(app, route_prefix='/admin/')
    admin.other_ad.ListView.register(app, route_prefix='/admin/')
    admin.other_ad.EditView.register(app, route_prefix='/admin/')
    admin.other_ad.CustomAdListView.register(app, route_prefix='/admin/')
    admin.other_ad.CustomadDeleteView.register(app, route_prefix='/admin/')
    admin.other_ad.CustomadAddView.register(app, route_prefix='/admin/')

    api.iphone.HomePageView.register(app, route_prefix='/api/')
    api.ipad.HomePageView.register(app, route_prefix='/api/')
    api.app.DetailView.register(app, route_prefix='/api/')
    api.app.RelatedView.register(app, route_prefix='/api/')
    api.app.ListView.register(app, route_prefix='/api/')
    api.app.CheckUpdateView.register(app, route_prefix='/api/')
    api.app.SearchView.register(app, route_prefix='/api/')
    api.app_topic.ListView.register(app, route_prefix='/api/')
    api.app_topic.DetailView.register(app, route_prefix='/api/')
    api.app_genre.ListView.register(app, route_prefix='/api/')
    api.client.UpdateView.register(app, route_prefix='/api/')
    api.client.PlistView.register(app, route_prefix='/api/')
    api.language.ListView.register(app, route_prefix='/api/')
    api.hotword.ListView.register(app, route_prefix='/api/')
    api.app_ad_image.ListView.register(app, route_prefix='/api/')
    api.other_ad.InfoView.register(app, route_prefix='/api/')
    api.web_on.WebOnView.register(app, route_prefix='/api/')
    api.app_collection.AppListView.register(app, route_prefix='/api/')
    api.notification.ListView.register(app, route_prefix='/api/')
