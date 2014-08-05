#encoding=UTF-8
from flask.ext.script import Manager

from main import app, register_view

from scripts.update_app_info import *
from scripts.indexer import build_search_index_run
from scripts.cache_app import cache_app_run
from scripts.cache_app_list import cache_app_list_run
from scripts.compare_update import track_need_to_update
from scripts.sync_app_CN import fetch_appbase

manager = Manager(app)
register_view()


@manager.command
def build_search_index(): build_search_index_run()

@manager.option('-I', '--ID', help='App mongo obejct id ')
def cache_app(ID): cache_app_run(ID)

@manager.option('-G', '--genreID', help='App genre id ')
def cache_app_list(genreID):
    cache_app_list_run(genreID)

@manager.command
def update_app(): recursive_update_app_info()

@manager.command
def compare_update():
	track_need_to_update()

@manager.command
def sync_app_info():
	fetch_appbase()

if __name__ == '__main__':
    manager.run()
