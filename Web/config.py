import web

web.config.debug = False
#web.config.debug = True

VERSION = '0.1 git commit 12'

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
}

LANGUAGELIST = {
    1:      'C',
    2:      'C++',
    3:      'Free Pascsl',
}

urls = (
    '/',                'Index',
    '/register/(.*)',   'Register',
    '/login/(.*)',      'Login',
    '/logout/(.*)',     'Logout',
    '/problem/(.*)',    'ProblemList',
    '/submit/(.*)',     'Submit',
    '/newproblem/(.*)', 'NewProblem',
    '/p(.*)',           'Problem',
    '/status/(.*)',     'Status',
    '/s(.*)',           'ShowSource',
    '/layout','layout',
)

web.config.session_parameters['cookie_name'] = 'cofun_session'
web.config.session_parameters['timeout'] = 3600*24*7
web.config.session_parameters['ignore_expiry'] = True
web.config.session_parameters['ignore_change_ip'] = True
web.config.session_parameters['secret_key'] = 'fL|Christiana@fxqXtfN%Blake(ldA0A0J'
