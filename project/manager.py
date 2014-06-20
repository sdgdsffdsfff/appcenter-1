from scripts.update_app_info import update_app_info
from flask.ext.script import Manager
from main import app, register_view
from indexer import index_app

manager = Manager(app)
register_view()


@manager.command
def index(): index_app()

@manager.command
def update_app(): update_app_info()

if __name__ == '__main__':
    manager.run()
