from flask.ext.script import Manager
from main import app, register_view
from indexer import index_app

manager = Manager(app)
register_view()

@manager.command
def index(): index_app()

if __name__ == '__main__':
    manager.run()
