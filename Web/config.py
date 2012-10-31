import web

web.config.debug = False
#web.config.debug = True

VERSION = '0.1 git commit 27'

CONFIG = {
    'dbtype':       'mysql',
    'dbuser':       'root',
    'dbpasswd':     '123456',
    'dbname':       'cofun',
    'statusrows':   25,
    'problemrows':  30,
}

RESULTLIST = {
    0:      '<span class="label">Waiting</span>',
    1:      '<span class="label label-info">Compile Error</span>',
    2:      '<span class="label">Running & Judging</span>',
    3:      '<span class="label label-success">Accepted</span>',
    4:      '<span class="label label-important">Wrong Answer</span>',
    5:      '<span class="label label-inverse">Runtime Error</span>',
    6:      '<span class="label label-warning">Time Limit Exceeded</span>',
    7:      '<span class="label label-warning">Memory Limit Exceeded</span>',
  100:      'Running<span class="badge badge-important">%d</span>',
   -1:      '<span class="label">Hidden</span>',
}

LANGUAGELIST = {
    1:      'C',
    2:      'C++',
    3:      'Free Pascal',
}

urls = (
    '/',                'Index',
    '/register/(.*)',   'Register',
    '/login/(.*)',      'Login',
    '/logout/(.*)',     'Logout',
    '/problem/(.*)',    'ProblemList',
    '/submit/(\d*)',     'Submit',
    '/submit/(\d+)/(\d+)','Submit',
    '/newproblem/(.*)', 'NewProblem',
    '/p(\d+)',           'Problem',
    '/status/(\d*)',     'Status',
    '/status/(\d*)(ajax){1}',     'Status',
    '/s(\d+)',          'ShowSource',
    '/contest/(\d*)',    'ContestList',
    '/c(\d+)p(.\d+)',   'ContestProblem',
    '/c(\d+)',        'Contest',
    '/cr(\d+)',         'ContestRank',
    '/newcontest/(.*)', 'NewContest',
    '/whatsnew/(.*)',   'WhatsNew',
    '/upload/(.*)',     'Upload',
    '/series/(.*)',     'SeriesList',
    '/series(\d+)',     'Series',
    '/series(\d+)/rank','SeriesRank',
    '/series(\d+)/rank(ajax){1}',     'SeriesRank',
    '/newseries/(.*)',  'NewSeries',
    '/status/(\d*)',     'Status',
    '/ajax/watch/(.*)',     'AjaxWatchStatus',
)

web.config.session_parameters['cookie_name'] = 'cofun_session'
web.config.session_parameters['timeout'] = 3600*24*7
web.config.session_parameters['ignore_expiry'] = True
web.config.session_parameters['ignore_change_ip'] = True
web.config.session_parameters['secret_key'] = 'fL|Christiana@fxqXtfN%Blake(ldA0A0J'
