from __future__ import with_statement
from fabric.api import run, sudo, env, local, cd, require, abort, put
from fabric.contrib.files import exists
from fabric.contrib.project import rsync_project
import time

env.repository = 'git@github.com:bcochran/disciple.git'
env.branch = 'origin/master'
env.hosts = ['bencochran@slice.gnar.us']
# the parent directory of our deployment
env.deploy_to = '/home/bencochran/'

def deploy():
    require('deploy_to')
    
    rsync_project(env.deploy_to, exclude="*.pyc")
    # sudo('chmod -R gnarus %(deploy_to)s/diciple' % env)
    restart()

def restartOne(n):
    if not exists('/service/disciple%s' % n):
        sudo('ln -s /home/bencochran/disciple/runners/disciple%s /service/disciple%s' % (n, n))

    if exists('/tmp/fcgi-disciple-%s.socket' % n):
        sudo('sudo svc -t /service/disciple%s; rm /tmp/fcgi-disciple-%s.socket' % (n, n))
    else:
        sudo('sudo svc -t /service/disciple%s' % n)

    time.sleep(1)
    return exists('/tmp/fcgi-disciple-%s.socket' % n)

def restart():
    for n in range(1,5):
        if not restartOne(n):
            print 'Server %s failed to start. Aborting deployment!' % n
            break
            
    # add checking to see if they correctly restart before moving to the next
    # sudo('sudo svc -t /service/disciple1')
    # sudo('sudo svc -t /service/disciple2')
    # sudo('sudo svc -t /service/disciple3')
    # sudo('sudo svc -t /service/disciple4')
