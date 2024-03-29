from fabric.api import local
from fabric.api import *

env.roledefs['test_web_server'] = ['ops@192.168.2.241:22']

env.passwords = {
    'ops@192.168.2.241:22': '2wsx1qaz',
}

@roles("test_web_server")
def deploy_test():
    project_dir = '/home/ops/appcenter/project'
    with cd(project_dir):
        run('git pull')
        run("sudo supervisorctl restart appcenter")
