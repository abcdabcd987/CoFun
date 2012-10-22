import re
import web
import db
import random
from config import * 


app = web.application(urls, globals())
session = web.session.Session(app, web.session.DiskStore('Sessions'), initializer={'userid': -1, 'username': None, 'gravatar': None})
render = web.template.render('Templates/', globals=globals(), base='Layout')

vtitle = re.compile(r'.{2,100}$')
vtime = re.compile(r'^\d{3,6}$')
vmemory = re.compile(r'^\d{3,6}$')
vname = re.compile(r".{4,50}$")
vpwd = re.compile(r".{4,}$")
vemail = re.compile(r".+@.+")

class Index:
    def GET(self):
        return render.Index()

class Register:
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
        if not username or not vname.match(username):
            return render.Register('UserName must be between 4 to 50 characters')
        if not vpwd.match(password):
            return render.Register('Password must be more than 4 characters')
        if not email or not vemail.match(email):
            return render.Register('Invaild Email address')

        email = email.lower()
        userid = db.Member.Add(username, password, email)
        if userid:
            session.userid = userid
            session.username = username
            session.gravatar = db.Utility.MD5(email)
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
        username = i.get('Username', ' ')
        password = i.get('Password', ' ')
        userid = db.Member.GetID(username)
        if userid:
            info = db.Member.GetInfo(userid)
            if db.Utility.SHA1(password) == info['UserPassword']:
                session.userid = userid
                session.username = username
                session.gravatar = db.Utility.MD5(info['UserEmail'].lower())
                raise web.seeother('/')
        return render.Login('Username or Password Errors!')

class Logout:
    def GET(self, arg):
        session.userid = -1
        session.username = None
        raise web.seeother('/')

class NewProblem:
    def GET(self, arg):
        if session.userid == -1:
            raise web.seeother('/')
        return render.NewProblem()

    def POST(self, arg):
        if session.userid == -1:
            raise web.seeother('/')
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
        if not title or not vtitle.match(title):
            return render.NewProblem('Title must be between 2 to 100 characters.')
        if not time or not vtime.match(time):
            return render.NewProblem('Time Limit must be between 100 and 999999.')
        if not memory or not vmemory.match(time):
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
        try:
            page = int(arg)
        except:
            page = 1
        count = (db.Problem.Count()+CONFIG['problemrows']-1)//CONFIG['problemrows']
        page = min(page, count)
        page = max(page, 1)
        return render.ProblemList(db.Problem.GetList((page-1)*CONFIG['problemrows'], CONFIG['problemrows']), page, count)

class Problem:
    def GET(self, problemid):
        return render.Problem(db.Problem.Get(int(problemid)))

class Submit:
    def GET(self, problemid):
        if session.userid == -1:
            raise web.seeother('/')
        lang = db.Member.GetLastLanguage(session.userid)
        return render.Submit(problemid, lang)

    def POST(self, arg):
        if session.userid == -1:
            raise web.seeother('/')
        i = web.input()
        problemid = i.get("ProblemID", None)
        language = i.get("SubmitLanguage", None)
        code = i.get("SubmitCode", None)
        if not language:
            return render.Submit(problemid, 'Must select a language')
        if not code:
            return render.Submit(problemid, 'Must submit some code')
        if not problemid or not db.Problem.Exist(int(problemid)):
            return render.Submit(problemid, 'Problem Does Not Exist')
        db.Status.Submit(problemid, 0, session.userid, language, code)
        raise web.seeother('/status/')

class Status:
    def GET(self, arg):
        try:
            page = int(arg)
        except:
            page = 1
        count = (db.Status.Count()+CONFIG['statusrows']-1)//CONFIG['statusrows']
        page = min(page, count)
        page = max(page, 1)
        return render.Status(db.Status.GetList((page-1)*CONFIG['statusrows'], CONFIG['statusrows']), page, count)

class ShowSource:
    def GET(self, submitid):
        (results, detail, avgmem, sumtime) = db.Status.Detail(int(submitid))
        return render.ShowSource(detail, results, int(avgmem) if avgmem else 0, int(sumtime) if sumtime else 0)

if __name__ == '__main__':
    app.run()
