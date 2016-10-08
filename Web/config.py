#-*- coding: utf-8 -*-
import web
import cgi

web.config.debug = False
#web.config.debug = True

VERSION = '2014-11-19'

CONFIG = {
    'dbtype':       'mysql',
    'dbuser':       'root',
    'dbpasswd':     'yourpasswd',
    'dbname':       'cofun',
    'statusrows':   25,
    'problemrows':  50,
    'rankrows':     50,
    'contestcurrentrankrows':50,
    'seriesrankrows':50,
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
    8:      '<span class="label label-warning">Data Config Error</span>',
    9:      '<span class="label label-inverse">SPJ Error</span>',
  100:      'Running<span class="badge badge-important">%d</span>',
   -1:      '<span class="label">Hidden</span>',
}

ALERTLIST = {
   -1:      None,
    0:      None,
    1:      'alert alert-info',
    2:      None,
    3:      'alert alert-success',
    4:      'alert alert-error',
    5:      'alert alert-error',
    6:      'alert',
    7:      'alert',
    8:      'alert',
    9:      'alert alert-error',
}

LANGUAGELIST = {
    1:      'C',
    2:      'C++',
    3:      'Free Pascal',
}

USERCOLOR = {
    1:      'user-gray',
    2:      'user-green',
    3:      'user-blue',
    4:      'user-violet',
    5:      'user-violet',
    6:      'user-orange',
    7:      'user-orange',
    8:      'user-red',
}

USERTITLE = {
    1:      '下水道',#'Pupil',
    2:      '普通',#'Specialist',
    3:      '上水道',#'Expert',
    4:      '勇者',#'Candidate Master',
    5:      '来自异界的',#'Candidate Master',
    6:      '传说',#'Master',
    7:      '史诗',#'International master',
    8:      '王者',#'Grandmaster',
}

urls = (
    '/',                          'Index',
    '/register/(.*)',             'Register',
    '/login/(.*)',                'Login',
    '/logout/(.*)',               'Logout',
    '/problem/(.*)',              'ProblemList',
    '/submit/(\d*)',              'Submit',
    '/submit/(\d+)/(\d+)',        'Submit',
    '/newproblem/(.*)',           'NewProblem',
    '/p(\d+)',                    'Problem',
    '/status/(\d*)',              'Status',
    '/status/(\d*)(ajax){1}',     'Status',
    '/s(\d+)',                    'ShowSource',
    '/contest/(\d*)',             'ContestList',
    '/c(\d+)p(.\d+)',             'ContestProblem',
    '/c(\d+)',                    'Contest',
    '/cr(\d+)',                   'ContestRank',
    '/c(\d+)/rank/(\d*)',         'ContestCurrentRank',
    '/c(\d+)/rank/(\d*)(ajax){1}','ContestCurrentRank',
    '/newcontest/(.*)',           'NewContest',
    '/whatsnew/(.*)',             'WhatsNew',
    '/upload/(.*)',               'Upload',
    '/series/(.*)',               'SeriesList',
    '/series(\d+)',               'Series',
    '/series(\d+)/rank/(\d*)',    'SeriesRank',
    '/series(\d+)/rank/(\d*)(ajax){1}', 'SeriesRank',
    '/newseries/(.*)',            'NewSeries',
    '/ajax/watch/(.*)',           'AjaxWatchStatus',
    '/ep(\d+)',                   'EditProblem',
    '/ec(\d+)',                   'EditContest',
    '/eseries(\d+)',              'EditSeries',
    '/download/p(\d+)t(\d+)(.*)', 'TestdataDownload',
    '/testdata/p(\d+)t(\d+)',     'Testdata',  
    '/modifyuser/(.*)',           'ModifyUser',
    '/uploaddata/p(\d+)t(\d+)m(\d+)',          'UploadData',
    '/faq/(.*)',                  'FAQ',
    '/u(\d+)',                    'UserInfo',
    '/ranklist/(.*)',             'RankList',
)

web.config.session_parameters['cookie_name'] = 'cofun_session'
web.config.session_parameters['timeout'] = 3600*24*7
web.config.session_parameters['ignore_expiry'] = True
web.config.session_parameters['ignore_change_ip'] = True
web.config.session_parameters['secret_key'] = 'fL|Christiana@fxqXtfN%Blake(ldA0A0J'

DATA_DIR = '/home/cofun/data/%d/'
SPJ = DATA_DIR + 'spj'
SPJFILE = {
    1:  DATA_DIR + 'spj.c',
    2:  DATA_DIR + 'spj.cc',
    3:  DATA_DIR + 'spj.pas',
}
COMPILE_COMMAND = {
    1:  'gcc ' + DATA_DIR + 'spj.c -o ' + DATA_DIR + 'spj -Wall',
    2:  'g++ ' + DATA_DIR + 'spj.cc -o ' + DATA_DIR + 'spj -Wall',
    3:  'fpc ' + DATA_DIR + 'spj.pas -o' + DATA_DIR + 'spj -vewh -Tlinux',
}
COMPILE_REWRITE = ' 1> ' + DATA_DIR + '__compile_info.txt 2>&1'
COMPILE_INFO = DATA_DIR + '__compile_info.txt'

def GetRatingLevel(Rating):
    x = 8
    if Rating < 1200:
        x = 1
    elif Rating < 1500:
        x = 2
    elif Rating < 1700:
        x = 3
    elif Rating < 1800:
        x = 4
    elif Rating < 1900:
        x = 5
    elif Rating < 2050:
        x = 6
    elif Rating < 2200:
        x = 7
    return x

def GetColor(Rating):
    return USERCOLOR[GetRatingLevel(Rating)]

def GetTitle(Rating):
    return USERTITLE[GetRatingLevel(Rating)]

def GetUserHtml(Rating, UserName, UserID, RealName=None, Str=None):
    if not Str:
        Str = ''
    if not RealName:
        return '<a href="/u%s" class="%s" title="%s %s">%s</a>' % (UserID, GetColor(Rating), GetTitle(Rating), cgi.escape(UserName).replace(' ','&nbsp;'), Str + cgi.escape(UserName).replace(' ','&nbsp;'))
    else:
        return '<a href="/u%s" class="%s" title="%s %s">%s(%s)</a>' % (UserID, GetColor(Rating), GetTitle(Rating), cgi.escape(UserName).replace(' ','&nbsp;'), Str + cgi.escape(UserName).replace(' ','&nbsp;'), cgi.escape(RealName).replace(' ','&nbsp;'))

