from fabric.api import local
from fabric.api import *

env.roledefs['test_web_server'] = ['ops@192.168.2.240:22']

env.passwords = {
    'ops@192.168.2.240:22': '2wsx1qaz',
}

@roles("test_web_server")
def deploy_test():
    project_dir = '/data0/wwwroot/appcenter/project'
    with cd(project_dir):
        run('git pull')
        run("pkill -f 'python manager.py runserver'")
        run("nohup python manager.py runserver --threaded --host 0.0.0.0 --port 5000 &")
