'''
Early stages of development of a GitHub project tracker. It's like watching a 
live birth. But messier.
'''

import sys

from github import github
from bop import *
import memcache
import iso8601

import config
from helpers import AttrDict

__version__ = "0.1"

@setup
def setup_cache():
    cache = memcache.Client(['127.0.0.1:11211'])
    
    if env('clear_cache'):
        cache.delete('disciple_repos')
    
    # dicts returned from setup functions are added to the app's Bop
    # environment
    return {'cache': cache}

@setup
def setup_template():
    return {'template.engine': 'jinja2', 'template.path': ['templates']}

@get('/')
def index(request):
    cache = env('cache')
    repos = cache.get('disciple_repos')
    
    if not repos:
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
            for commit in commits:
                committed_date = iso8601.parse_date(commit.committed_date)
                commit.committed_date = committed_date.strftime('%a %b %d %H:%M:%S %z %Y')
                authored_date = iso8601.parse_date(commit.authored_date)
                commit.authored_date = authored_date.strftime('%a %b %d %H:%M:%S %z %Y')
                
            repos.append(AttrDict({'info':info, 'commits':commits}))
        
        # cache it for 10 minutes
        cache.set("disciple_repos", repos, time=600)
    
    return render('overview.html', repos=repos) # 200 OK; text/html is default

if __name__ == '__main__':
    run()
