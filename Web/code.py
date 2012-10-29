import re
import web
import db
import zlib
import time
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
        return render.ProblemList(db.Problem.GetList((page-1)*CONFIG['problemrows'], CONFIG['problemrows'], session.userid), page, count)

class Problem:
    def GET(self, problemid):
        try:
            problemid = int(problemid)
        except:
            problemid = 0
        if db.Contest.IsProblemNotDone(problemid):
            return render.Problem(None)
        return render.Problem(db.Problem.Get(int(problemid)))

class Submit:
    def GET(self, problemid, contestid=0):
        if session.userid == -1:
            raise web.seeother('/')
        lang = db.Member.GetLastLanguage(session.userid)
        return render.Submit(problemid, contestid, lang)

    def POST(self, pid, cid=0):
        if session.userid == -1:
            raise web.seeother('/')
        i = web.input()
        problemid = i.get("ProblemID", 0)
        language = i.get("SubmitLanguage", None)
        code = i.get("SubmitCode", None)
        contestid = i.get("ContestID", 0)
        lang = db.Member.GetLastLanguage(session.userid)
        if not language:
            return render.Submit(problemid, contestid, lang, 'Must select a language')
        if not code:
            return render.Submit(problemid, contestid, lang, 'Must submit some code')
        if not problemid or not db.Problem.Exist(int(problemid)):
            return render.Submit(problemid, contestid, lang, 'Problem Does Not Exist')
        if contestid != 0 and db.Contest.GetStatusByID(contestid) != 2:
            return render.Submit(problemid, contestid, lang, 'Contest is not LIVE')
        if db.Contest.IsProblemNotDone(problemid, int(contestid)):
            return render.Submit(problemid, contestid, lang, 'Problem Does Not Exist or Hidden')
        db.Status.Submit(problemid, contestid, session.userid, language, code)
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
        lst = db.Status.GetList((page-1)*CONFIG['statusrows'], CONFIG['statusrows'])
        for record in lst:
            if record.ContestID != 0:
                status = db.Contest.GetStatusByID(record.ContestID)
                if status != 3:
                    record.SubmitStatus = -1
        return render.Status(lst, page, count)
        #return lst

class ShowSource:
    def GET(self, submitid):
        try:
            submitid = int(submitid)
        except:
            submitid = -1
        (results, detail, avgmem, sumtime) = db.Status.Detail(int(submitid))
        if detail.ContestID != 0:
            status = db.Contest.GetStatusByID(detail.ContestID)
            if status != 3:
                detail.SubmitStatus = -1
        return render.ShowSource(detail, results, int(avgmem) if avgmem else 0, int(sumtime) if sumtime else 0)

class NewContest:
    def GET(self, arg):
        if session.userid == -1:
            raise web.seeother('/')
        return render.NewContest()
    def POST(self, arg):
        if session.userid == -1:
            raise web.seeother('/')
        i = web.input()
        title = i.get('ContestTitle', None)
        stime = i.get('ContestStime', None)
        etime = i.get('ContestEtime', None)
        desc = i.get('ContestDescription', None)
        prin = i.get('ContestPrincipal', None)
        prob = i.get('ProblemList', None)
        mesg = None
        if not title or not vtitle.match(title):
            mesg = 'Contest Title must be between 2 and 50 characters'
        if not desc:
            mesg = 'Contest Description can\'t be empty'
        if not prin:
            mesg = 'There must be one principal'
        else:
            userid = db.Member.GetID(prin)
            if not userid:
                mesg = '[%s] does NOT exist' % prin
        if not prob:
            mesg = 'There is no problem appointed'
        try:
            starttime = time.strptime(stime, '%Y-%m-%d %H:%M:%S')
        except:
            mesg = '[%s] is invaild' % stime
        try:
            endtime = time.strptime(etime, '%Y-%m-%d %H:%M:%S')
        except:
            mesg = '[%s] is invaild' % etime
        if mesg:
            return render.NewContest(mesg)

        res = db.Contest.Add(title, stime, etime, desc, userid, prob.strip().split('|'))
        if res:
            return render.NewContest('Success! The new contest ID is: ' + str(res))
        else:
            return render.NewContest('Failed!')

class ContestList:
    def GET(self, arg):
        try:
            page = int(arg)
        except:
            page = 1
        count = (db.Contest.Count()+CONFIG['problemrows']-1)//CONFIG['problemrows']
        page = min(page, count)
        page = max(page, 1)
        res = db.Contest.GetList((page-1)*CONFIG['problemrows'], CONFIG['problemrows'])
        if res:
            for contest in res:
                contest['ContestStatus'] = db.Contest.GetStatus(contest['ContestStartTime'], contest['ContestEndTime'])
                username = db.Member.GetInfo(contest['ContestPrincipal'])
                if not username:
                    username = '-1'
                contest['ContestPrincipal'] = username['UserName']
        return render.ContestList(res, page, count)

class Contest:
    def GET(self, contestid):
        try:
            contestid = int(contestid)
        except:
            contestid = 0
        (contest, problem) = db.Contest.Get(contestid)
        if not contest:
            return render.Contest(None, None, None)
        username = db.Member.GetInfo(contest.ContestPrincipal)
        if not username:
            username = 'empty'
        contest.ContestPrincipal = username['UserName']
        contest['ContestStatus'] = db.Contest.GetStatus(contest.ContestStartTime, contest.ContestEndTime)
        return render.Contest(contest, problem)

class ContestProblem:
    def GET(self, contestid, problemid):
        try:
            contestid = int(contestid)
            problemid = int(problemid)
        except:
            contestid = 0
            problemid = 0
        (contest, problem) = db.Contest.GetProblem(contestid, problemid)
        if not contest or not problem:
            return render.ContestProblem(None, None)
        username = db.Member.GetInfo(contest.ContestPrincipal)
        if not username:
            username = 'empty'
        contest.ContestPrincipal = username['UserName']
        contest['ContestStatus'] = db.Contest.GetStatus(contest.ContestStartTime, contest.ContestEndTime)
        return render.ContestProblem(contest, problem)

class ContestRank:
    def GET(self, contestid):
        try:
            contestid = int(contestid)
        except:
            contestid = -1
        (contest, problem) = db.Contest.Get(contestid)
        if not contest:
            return render.ContestRank(None, None)
        if db.Contest.GetStatusByID(contestid) != 3:
            return render.ContestRank(None, None)
        username = db.Member.GetInfo(contest.ContestPrincipal)
        if not username:
            username = 'empty'
        contest.ContestPrincipal = username['UserName']
        contest['ContestStatus'] = db.Contest.GetStatus(contest.ContestStartTime, contest.ContestEndTime)

        rank = db.Contest.GetRank(contestid)
        return render.ContestRank(contest, rank)

class WhatsNew:
    def GET(self, arg):
        return render.WhatsNew()

class Upload:
    def GET(self, arg):
        if session.userid == -1:
            raise web.seeother('/')
        return render.Upload()

    def POST(self, arg):
        if session.userid == -1:
            raise web.seeother('/')
        i = web.input(UploadFile={})
        filedir = 'static/probimg/'
        if 'UploadFile' in i:
            filepath = i.UploadFile.filename.replace('\\', '/')
            extension = filepath.split('/')[-1].split('.')[-1].lower()
            if extension not in ('jpg', 'png', 'gif'):
                return render.Upload('Must be a image')
            rand = '%x' % (zlib.crc32(str(random.random())) & 0xffffffff)
            filename = time.strftime('%Y%m%d_%H%M%S_'+rand+'.'+extension)
            fout = open(filedir+'/'+filename, 'wb')
            fout.write(i.UploadFile.file.read())
            fout.close()
        return render.Upload('Done! See <code>http://cofun.org/static/probimg/'+filename+'</code>')


###Series
class NewSeries:
    def GET(self, arg):
        if session.userid == -1:
            raise web.seeother('/')
        return render.NewSeries()
    def POST(self, arg):
        if session.userid == -1:
            raise web.seeother('/')
        i = web.input()
        title = i.get('SeriesTitle', None)
        desc = i.get('SeriesDescription', None)
        prob = i.get('ProblemList', None)
        mesg = None
        if not title or not vtitle.match(title):
            mesg = 'Series Title must be between 2 and 50 characters'
        if not desc:
            mesg = 'Series Description can\'t be empty'
        if not prob:
            mesg = 'There is no problem appointed'
        if mesg:
            return render.NewSeries(mesg)

        res = db.Series.Add(title, desc, prob.strip().split('|'))
        if res:
            return render.NewSeries('Success! The new series ID is: ' + str(res))
        else:
            return render.NewSeries('Failed!')

class SeriesList:
    def GET(self, arg):
        try:
            page = int(arg)
        except:
            page = 1
        count = (db.Series.Count()+CONFIG['problemrows']-1)//CONFIG['problemrows']
        page = min(page, count)
        page = max(page, 1)
        res = db.Series.GetList((page-1)*CONFIG['problemrows'], CONFIG['problemrows'])
        return render.SeriesList(res, page, count)

class Series:
    def GET(self, seriesid):
        try:
            seriesid = int(seriesid)
        except:
            seriesid = 0
        (series, problem) = db.Series.Get(seriesid, session.userid)
        if not series:
            return render.Series(None, None, None)
        return render.Series(series, problem)

class SeriesRank:
    def GET(self, seriesid):
        try:
            seriesid = int(seriesid)
        except:
            seriesid = -1
        (series, problem) = db.Series.Get(seriesid)
        if not series:
            return render.SeriesRank(None, None)
        rank = db.Series.GetRank(seriesid)
        return render.SeriesRank(series, rank)


if __name__ == '__main__':
    app.run()
