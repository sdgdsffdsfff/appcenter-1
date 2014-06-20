from fabric.api import local
from fabric.api import *

env.roledefs['web_server'] = ['zsf@61.155.215.53:58422', 'zsf@61.155.215.54:58422']

env.passwords = {
    'zsf@61.155.215.53:58422': 'aPp6vv_c7om',
    'zsf@61.155.215.54:58422': 'aPp6vv_c7om'
}

def pcode():
    local('git add --all && git pull && git commit -m "Fix" -a && git push')

@roles("web_server")
def deploy_web():
    project_dir = '/data0/www/appcenter/project'
    with cd(project_dir):
        run('git pull')
        run('kill -9 $(cat /tmp/appcenter_uwsgi.pid)')
        run('uwsgi appcenter.ini')

def deploy():
    execute(deploy_web)
