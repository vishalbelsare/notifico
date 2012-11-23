# -*- coding: utf8 -*-
import os.path

from fabric.api import *
from fabric.contrib.project import rsync_project
from fabric.contrib.files import exists

# the user used for the server process
env.user = 'tyler'

# the host groups to deploy to
env.roledefs = {
    'web': [
        'n.tkte.ch'
    ],
    'db': [
        'n.tkte.ch'
    ]
}


def www_root():
    """
    Returns the directory used to store the frontent project.
    """
    return os.path.abspath(os.path.join(
        '/home',
        env.user
    ))


@roles('web')
def deploy_web():
    """
    Deploys the frontend project (http).
    """
    # Update the source files.
    rsync_project(
        remote_dir=www_root(),
        local_dir=os.path.abspath('./frontend')
    )

    with cd(www_root()):
        # Update the SQLAlchemy tables.
        # run('python -m notifico.deploy.build')

        if exists('notifico.pid'):
            run('kill -HUP `cat notifico.pid`')
        else:
            run(' '.join([
                'gunicorn',
                '-w 4',
                '-b 127.0.0.1:4000',
                '-p notifico.pid',
                '--daemon',
                 '"frontend:start(debug=False)"'
            ]))


@roles('web')
def init_web():
    """
    Helper to set up a new frontent server.
    """
    # Make sure the latest source is on the server already.
    execute(deploy_web)

    # Install the minimum packages.
    sudo('apt-get install lighttpd')
    sudo('apt-get install python-pip')

    # Install our python dependencies.
    with cd(www_root()):
        p = os.path.join(www_root(), 'frontend', 'deploy', 'requirements.txt')
        sudo('pip install --requirement {0}'.format(p))


@roles('db')
def init_db():
    """
    Helper to set up a new db server.
    """
    suod('apt-get install redis')
