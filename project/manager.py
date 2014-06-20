from scripts.update_app_info import update_app_info
from flask.ext.script import Manager
from main import app, register_view
from scripts.indexer import build_search_index_run
from scripts.cache_app import cache_app_run
from scripts.cache_app_list import cache_app_list_run

manager = Manager(app)
register_view()


@manager.command
def build_search_index(): build_search_index_run()

#@manager.command
@manager.option('-I', '--ID', help='App mongo obejct id ')
def cache_app(ID): cache_app_run(ID)

@manager.command
def cache_app_list_run(genreID): cache_app_list_run(genreID)

@manager.command
def update_app(): update_app_info()

if __name__ == '__main__':
    manager.run()
