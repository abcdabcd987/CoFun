import re
import web
import db
import random
from config import render

urls = (
    '/',                'Index',
    '/register/(.*)',   'Register',
    '/login/(.*)',      'Login',
    '/logout/(.*)',     'Logout',
    '/problem/(.*)',    'ProblemList',
    '/submit/(.+)',     'Submit',
    '/newproblem/(.*)', 'NewProblem',
    '/p(\d{4,})',       'Problem',
)

app = web.application(urls, globals())
session = web.session.Session(app, web.session.DiskStore('Sessions'), initializer={'userid': -1, 'username': None})

class Index:
    def GET(self):
        return render.Index(session.userid, session.username)

class Register:
    vname = re.compile(r".{4,50}$")
    vpwd = re.compile(r".{4,}$")
    vemail = re.compile(r".+@.+")

    def GET(self, arg):
        if session.userid == -1:
            return render.Register()
        else:
            raise web.seeother('/')

    def POST(self, arg):
        if session.userid != -1:
            raise web.seeother('/')
        i = web.input()
        username = i.get('Username', None)
        password = i.get('Password', None)
        repassword = i.get('RePassword', None)
        email = i.get('Email', None)
        if not password or not repassword or not password == repassword:
            return render.Register("Passwords don't match")
        if not username or not Register.vname.match(username):
            return render.Register('UserName must be between 4 to 50 characters')
        if not Register.vpwd.match(password):
            return render.Register('Password must be more than 4 characters')
        if not email or not Register.vemail.match(email):
            return render.Register('Invaild Email address')

        userid = db.Member.Add(username, password, email)
        if userid:
            session.userid = userid
            session.username = username
            raise web.seeother('/')
        else:
            return render.Register('['+username+'] or ['+email+'] exists')

class Login:
    def GET(self, arg):
        if session.userid == -1:
            return render.Login()
        else:
            raise web.seeother('/')

    def POST(self, arg):
        if session.userid != -1:
            raise web.seeother('/')
        i = web.input()
        username = i.get('Username', None)
        password = i.get('Password', None)
        userid = db.Member.GetID(username)
        if userid and db.Utility.SHA1(password) == db.Member.GetPassword(userid):
            session.userid = userid
            session.username = username
            raise web.seeother('/')
        else:
            return render.Login('Username or Password Errors!')

class Logout:
    def GET(self, arg):
        session.userid = -1
        session.username = None
        raise web.seeother('/')

class NewProblem:
    vtitle = re.compile(r'.{4,100}$')
    vtime = re.compile(r'^\d{3,6}$')
    vmemory = re.compile(r'^\d{3,6}$')
    def GET(self, arg):
        return render.NewProblem()

    def POST(self, arg):
        i = web.input()
        title = i.get('ProblemTitle', None)
        time = i.get('ProblemTime', None)
        memory = i.get('ProblemMemory', None)
        desc = i.get('ProblemDescription', None)
        formatin = i.get('ProblemInput', None)
        formatout = i.get('ProblemOutput', None)
        samplein = i.get('ProblemSampleIn', None)
        sampleout = i.get('ProblemSampleOut', None)
        hint = i.get('ProblemHint', None)
        source = i.get('ProblemSource', None)
        if not title or not NewProblem.vtitle.match(title):
            return render.NewProblem('Title must be between 4 to 100 characters.')
        if not time or not NewProblem.vtime.match(time):
            return render.NewProblem('Time Limit must be between 100 and 999999.')
        if not memory or not NewProblem.vmemory.match(time):
            return render.NewProblem('Memory Limit must be between 100 and 999999.')
        if not formatin:
            return render.NewProblem('Must have Input Format.')
        if not formatout:
            return render.NewProblem('Must have Output Format.')
        if not samplein:
            return render.NewProblem('Must have sample input.')
        if not sampleout:
            return render.NewProblem('Must have sample output.')
        problemid = db.Problem.Add(title, desc, formatin, formatout, samplein, sampleout, time, memory, hint, source)
        if problemid:
            return render.NewProblem('Added successfully! The new ProblemID is:'+str(problemid))
        else:
            return render.NewProblem('Failed!')

class ProblemList:
    def GET(self, arg):
        return render.ProblemList(db.Problem.GetList())

class Problem:
    def GET(self, problemid):
        return render.Problem(db.Problem.Get(int(problemid)))


if __name__ == '__main__':
    app.run()
