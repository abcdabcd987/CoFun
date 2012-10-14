import web

web.config.debug = False
render = web.template.render('Templates/', globals=globals())

CONFIG = {
    'dbtype':       'mysql',
    'dbuser':       'root',
    'dbpasswd':     '123456',
    'dbname':       'cofun',
}

RESULTLIST = {
    0:      'Waiting',
    1:      'Compile Error',
    2:      'Running & Judging',
    3:      'Accepted',
    4:      'Wrong Answer',
    5:      'Runtime Error',
    6:      'Time Limit Exceeded',
    7:      'Memory Limit Exceeded',
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
)
