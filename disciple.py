'''
Early stages of development of a GitHub project tracker. It's like watching a 
live birth. But messier.
'''

import sys
from optparse import OptionParser

from github import github
from bop import *


import config
from helpers import AttrDict

__usage__ = "%prog [options]"
__version__ = "0.1"

@get('/')
def index(request):
    try:
        gh = github.GitHub(config.username, config.token)
    except AttributeError, e:
        gh = github.GitHub()

    repos = []
    for repo in config.repos:
        info = gh.repos.show(repo.user, repo.repo)
        commits = gh.commits.forBranch(repo.user, repo.repo, repo.branch)
        if not isinstance(commits, list):
            commits = []
        repos.append(AttrDict({'info':info, 'commits':commits}))
    
    page = render('overview.html', repos=repos)
    return (200, {'Content-Type': 'text/html'}, page)

def main(args_in):
    p = OptionParser(description=__doc__, version=__version__)
    p.set_usage(__usage__)
    p.add_option("-d", "--development", action="store_true", 
        dest="development", help="run server in development mode")
    p.add_option("-n", "--number", type="int", dest="server_num",
        help="Server instance number")
    opt, args = p.parse_args(args_in)

    if not opt.server_num and not opt.development:
        p.error("either -d or -n are required")

    # set our bop environment
    root = get_root()
    root.env['template.engine'] = 'jinja2'
    root.env['template.path'] = ['templates/']

    if opt.development:
        run()
    else:
        socket = '/tmp/fcgi-disciple-%s.socket' % opt.server_num
        run('fastcgi', socket=socket, umask=0111)


if __name__=='__main__':
    main(sys.argv[1:])
