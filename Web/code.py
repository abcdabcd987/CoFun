#!/usr/bin/env python
#-*- coding: utf-8 -*-
import re
import contextlib
import os
import web
import db
import zlib
import time
import json
import random
import zipfile
import sys
from config import * 

reload(sys)  
sys.setdefaultencoding('utf-8')
global Uploading
Uploading = False
app = web.application(urls, globals())
session = web.session.Session(app, web.session.DiskStore('Sessions'), initializer={'userid': -1, 'username': None, 'gravatar': None})
render = web.template.render('Templates/', globals=globals(), base='Layout')
render_plain = web.template.render('Templates/', globals=globals())
render_plain2 = web.template.render('Templates/', globals=globals(), base='Layout2')

vtitle = re.compile(r'.{2,100}$')
vtime = re.compile(r'^\d{3,6}$')
vmemory = re.compile(r'^\d{3,6}$')
vname = re.compile(r".{3,15}$")
vrealname = re.compile(r".{2,15}$")
vsignature = re.compile(r".{0,200}$")
vpwd = re.compile(r".{4,}$")
vemail = re.compile(r".+@.+")


BUF_SIZE = 262144
class TestdataDownload:
    @staticmethod
    def GET_file_name(pid,tid,suf):
        basedir = '/home/cofun/data/%d/' % pid
        try:
            with open(basedir + 'data.config') as f:
                for line in f:
                    config = line.strip().split('|')
                    if not config:
                        continue
                    tid -= 1
                    if 0 == tid:
                        return config[suf]
        except:
            pass
        return None

    def GET(self,pid,tid,suf):
        if session.userid == -1:
            raise web.seeother('/')
        try:
            pid = int(pid)
        except:
            pid = 0
        if db.Contest.IsProblemNotDone(pid, 0, session.userid) or not db.Problem.Exist(pid):
            yield 'Problem Does Not Exist or Hidden'
            return

        try:
            tid = int(tid)
        except:
            tid = 0
        if tid <= 0:
            yield 'Testdata Does Not Exist'
            return

        if suf == 'in':
            suf = 0
        elif suf == 'out':
            suf = 1
        else:
            yield 'in or out?'
            return

        file_name = TestdataDownload.GET_file_name(pid,tid,suf)
        if not file_name:
            yield 'Testdata Not Found'
            return

        file_path = ('/home/cofun/data/%d/' % pid) + file_name
        try:
            with open(file_path, "rb") as f:
                web.header('Content-Type','application/octet-stream')
                web.header('Content-disposition', 'attachment; filename=%s' % file_name)
                while True:
                    c = f.read(BUF_SIZE)
                    if c:
                        yield c
                    else:
                        break
        except Exception, e:
            print e
            yield 'Error'

class Testdata:
    def GET(self,pid,tid):
        if session.userid == -1:
            return render.Testdata('','','Permission Denied')
        try:
            pid = int(pid)
        except:
            pid = 0
        if db.Contest.IsProblemNotDone(pid, 0, session.userid) or not db.Problem.Exist(pid):
            return render.Testdata('','','Problem Does Not Exist or Hidden')

        try:
            tid = int(tid)
        except:
            tid = 0
        if tid <= 0:
            return render.Testdata('','','Testdata Does Not Exist')
        
        In = TestdataDownload.GET_file_name(pid,tid,0)
        Out = TestdataDownload.GET_file_name(pid,tid,1)
        if not In or not Out:
            return render.Testdata('','','Testdata Does Not Exist')
        basedir = '/home/cofun/data/%d/' % pid
        try:
            with open(basedir + In) as In:
              with open(basedir + Out) as Out:
                s1 = In.read(500)
                s2 = Out.read(500)
                more1 = False
                more2 = False
                if In.read(1) != '': more1 = True
                if Out.read(1) != '': more2 = True
                return render.Testdata(s1,s2,'',more1,more2,pid,tid)
        except:
            return render.Testdata('','','Testdata Does Not Exist or Data Config Error')

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
        realname = i.get('Realname', None)
        password = i.get('Password', None)
        repassword = i.get('RePassword', None)
        email = i.get('Email', None)
        signature = i.get('Signature', None)
        if not password or not repassword or not password == repassword:
            return render.Register("Passwords don't match")
        if not username or not vname.match(username):
            return render.Register('UserName must be between 4 to 15 characters')
        if not realname:
            realname = username
        if not realname or not vrealname.match(realname):
            return render.Register('RealName must be between 2 to 15 characters')
        if not vpwd.match(password):
            return render.Register('Password must be more than 4 characters')
        if not email or not vemail.match(email):
            return render.Register('Invalid Email address')
        if not vsignature.match(signature):
            return render.Register('Signature must not exceed 200 characters')

        email = email.lower()
        userid = db.Member.Add(username, password, email, realname, signature)
        if userid:
            session.userid = userid
            session.username = username
            session.gravatar = db.Utility.MD5(email)
            raise web.seeother('/')
        else:
            return render.Register('['+username+'] or ['+email+'] exists')

class Login:
    def GET(self, arg):
        return render.Login()

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
                referer = web.ctx.env.get('HTTP_REFERER', '/')
                raise web.seeother(referer)
                #raise web.seeother('/')
        return render.Login('Username or Password Errors!')

class Logout:
    def GET(self, arg):
        if session.userid == -1:
            raise web.seeother('/')
        session.userid = -1
        session.username = None
        session.kill()
        referer = web.ctx.env.get('HTTP_REFERER', '/')
        raise web.seeother(referer)

class ModifyUser:
    def GET(self, arg):
        if session.userid != -1:
            return render.ModifyUser(db.Member.GetInfo(session.userid))
        else:
            raise web.seeother('/')

    def POST(self, arg):
        if session.userid == -1:
            raise web.seeother('/')
        i = web.input()
        username = db.Member.GetInfo(session.userid).UserName
        realname = i.get('Realname', None)
        password = i.get('Password', None)
        nepasswd = i.get('NePasswd', None)
        repasswd = i.get('RePasswd', None)
        signature = i.get('Signature', None)
        info = db.Member.GetInfo(session.userid)
        if db.Utility.SHA1(password) != info['UserPassword']:
            return render.ModifyUser(info, 'Incorrect Password!')
        if not nepasswd:
            nepasswd = password
        elif not nepasswd or not repasswd or not nepasswd == repasswd:
            return render.ModifyUser(info, "Passwords don't match")
        if not username or not vname.match(username):
            return render.ModifyUser(info, 'UserName must be between 4 to 15 characters')
        if not realname:
            realname = username
        if not vname.match(realname):
            return render.ModifyUser(info, 'RealName must be between 2 to 15 characters')
        if not vpwd.match(nepasswd):
            return render.ModifyUser(info, 'Password must be more than 4 characters')
        #if not email or not vemail.match(email):
            #return render.ModifyUser(info ,'Invalid Email address')
        #email = email.lower()
        if not vsignature.match(signature):
            return render.ModifyUser(info, 'Signature must not exceed 200 characters')
        userid = db.Member.Modify(session.userid, username, nepasswd, realname, signature)
        if userid:
            session.username = username
            #session.gravatar = db.Utility.MD5(email)
            return render.ModifyUser(db.Member.GetInfo(session.userid), 'Success!')
        return render.ModifyUser(info, '['+username+'] exists')

class NewProblem:
    def GET(self, arg):
        if session.userid == -1 or db.Member.GetLevel(session.userid) < 1:
            raise web.seeother('/')
        return render.NewProblem()

    def POST(self, arg):
        if session.userid == -1 or db.Member.GetLevel(session.userid) < 1:
            raise web.seeother('/')
        i = web.input()
        pid = db.Problem.NewID()
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
        spj = i.get('SpecialJudge', None)
        language = int(i.get("SubmitLanguage", None))
        code = i.get("SubmitCode", None)
        #datacfg = i.get('DataConfig', None)
        info = ''
        if spj == 'on':
            spj = 1
        else:
            spj = 0
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
        #if not datacfg:
            #return render.NewProblem('Must have Data Config.')
        if not code and spj:
            return render.NewProblem('Spj code can\'t be empty.')
        if spj:
            try:
                with open(SPJFILE[language] % pid, 'w') as f:
                    f.write(code)
                os.system(COMPILE_COMMAND[language] % (pid, pid) + COMPILE_REWRITE % pid)
                info = open(COMPILE_INFO % pid, 'r').read().replace(DATA_DIR % pid,'')
            except:
                pass
            if not os.path.exists(SPJ % pid):
                return render.NewProblem('Failed! Spj code compile error.', info)
        problemid = db.Problem.Add(title, desc, formatin, formatout, samplein, sampleout, time, memory, hint, source, spj)
        if problemid:
            raise web.seeother('/ep' + str(pid) +'#upload')
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
        if db.Contest.IsProblemNotDone(problemid,0,session.userid):
            return render.Problem(None)
        return render.Problem(db.Problem.Get(int(problemid)))

class UserInfo:
    def GET(self, uid):
        try:
            uid = int(uid)
        except:
            uid = 0
        (UserInfo, Problems) = db.Member.GetDetail(uid)
        Changes = db.Member.GetChanges(uid)
        Changespre = db.Member.GetChanges(db.Member.GetIDByRank(UserInfo._Rank - 1))
        Userpre = db.Member.GetInfo(db.Member.GetIDByRank(UserInfo._Rank - 1))
        Changesnxt = db.Member.GetChanges(db.Member.GetIDByRank(UserInfo._Rank + 1))
        Usernxt = db.Member.GetInfo(db.Member.GetIDByRank(UserInfo._Rank + 1))
        seed = int(time.mktime(time.strptime(time.strftime("%Y:%m:%d"), "%Y:%m:%d"))) // 24 // 60 // 60
        id = UserInfo["UserID"]
        seed = seed * 7 + 3 ** (id % 10) + (id // 10) * 107
        return render.UserInfo(UserInfo, Problems, Changes, seed, Changespre, Userpre, Changesnxt, Usernxt)

class RankList:
    def GET(self, page):
        try:
            page = int(page)
        except:
            page = 0
        count = (db.Member.Count()+CONFIG['rankrows']-1)//CONFIG['rankrows']
        page = min(page, count)
        page = max(page, 1)

        Rank = db.Member.GetRanklist((page-1)*CONFIG['rankrows'], CONFIG['rankrows'])
        return render.RankList(Rank, page, count)

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
        try:
            contestid = int(contestid)
        except:
            contestid = 0
        prin = db.Contest.GetPrincipal(contestid)
        lang = db.Member.GetLastLanguage(session.userid)
        if not language:
            return render.Submit(problemid, contestid, lang, 'Must select a language')
        if not code:
            return render.Submit(problemid, contestid, lang, 'Must submit some code')
        if not problemid or not db.Problem.Exist(int(problemid)):
            return render.Submit(problemid, contestid, lang, 'Problem Does Not Exist')
        if contestid != 0 and (db.Contest.GetStatusByID(contestid) != 2 and not db.Contest.IsPrincipal(contestid,session.userid)):
            return render.Submit(problemid, contestid, lang, 'Contest is not LIVE')
        if db.Contest.IsProblemNotDone(problemid, int(contestid), session.userid):
            return render.Submit(problemid, contestid, lang, 'Problem Does Not Exist or Hidden')
        db.Status.Submit(problemid, contestid, session.userid, language, code, prin)
        raise web.seeother('/status/')

class Status:
    def GET(self, arg, ajax=None):
        i = web.input()
        ProblemID = i.get('pid', '')
        UserName = i.get('uid', '')
        SubmitLanguage = i.get('lang', '')
        SubmitStatus = i.get('stat', '')
        ContestID = i.get('cid', '')
        try:
            if ProblemID != '':
                int(ProblemID)
        except:
            ProblemID = ''
        try:
            if ContestID != '':
                int(ContestID)
        except:
            ContestID = ''
        try:
            SubmitLanguage = int(SubmitLanguage)
        except:
            SubmitLanguage = '' 
        try:
            SubmitStatus = int(SubmitStatus)
        except:
            SubmitStatus = ''
        SubmitLanguage = str(SubmitLanguage)
        SubmitStatus = str(SubmitStatus)

        try:
            page = int(arg)
        except:
            page = 1
        count = (db.Status.Count(ProblemID=ProblemID, UserName=UserName, SubmitLanguage=SubmitLanguage, SubmitStatus=SubmitStatus, ContestID=ContestID, Prin=session.userid)+CONFIG['statusrows']-1)//CONFIG['statusrows']
        page = min(page, count)
        page = max(page, 1)

        lst = db.Status.GetList((page-1)*CONFIG['statusrows'], CONFIG['statusrows'], ProblemID=ProblemID, UserName=UserName, SubmitLanguage=SubmitLanguage, SubmitStatus=SubmitStatus, ContestID=ContestID, Prin=session.userid)
        wait = []
        if lst:
            for record in lst:
                if record.ContestID != 0:
                    status = db.Contest.GetStatusByID(record.ContestID)
                    if status != 3 and not db.Contest.IsPrincipal(record.ContestID,session.userid):
                        record.SubmitStatus = -1
                if record.SubmitStatus == 0 or record.SubmitStatus > 100:
                    wait.append(str(record.SubmitID))
        if ajax:
            ret = {}
            ret['html'] = render_plain.Status(lst, page, count, ProblemID, UserName, SubmitLanguage, SubmitStatus, ContestID, None, True).__body__
            ret['wait'] = '|'.join(wait)
            web.header("Content-Type","application/json; charset=utf-8")
            return json.dumps(ret)
        else:
            return render.Status(lst, page, count, ProblemID, UserName, SubmitLanguage, SubmitStatus, ContestID, '|'.join(wait))

class ShowSource:
    def GET(self, submitid):
        try:
            submitid = int(submitid)
        except:
            submitid = -1
        (results, detail) = db.Status.Detail(int(submitid))
        #if detail.ContestID != 0:
        #    status = db.Contest.GetStatusByID(detail.ContestID)
        #    if status != 3 and not db.Contest.IsPrincipal(detail.ContestID,session.userid):
        #        detail.SubmitStatus = -1
        if db.Contest.IsProblemNotDone(detail.ProblemID, 0, session.userid):
            detail.SubmitStatus = -1
        return render.ShowSource(detail, results)

class NewContest:
    def GET(self, arg):
        if session.userid == -1 or db.Member.GetLevel(session.userid) < 1:
            raise web.seeother('/')
        return render.NewContest()
    def POST(self, arg):
        if session.userid == -1 or db.Member.GetLevel(session.userid) < 1:
            raise web.seeother('/')
        i = web.input()
        title = i.get('ContestTitle', None)
        stime = i.get('ContestStime', None)
        etime = i.get('ContestEtime', None)
        desc = i.get('ContestDescription', None)
        prin = i.get('ContestPrincipal', None)
        prob = i.get('ProblemList', None)
        uprating = i.get('UpRating', 0.0)
        downrating = i.get('DownRating', 0.0)
        if db.Member.GetLevel(session.userid) < 10:
            uprating = 0.0
            downrating = 0.0
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

        (res, info) = db.Contest.Add(title, stime, etime, desc, userid, prob.strip().split('|'), uprating, downrating)
        if res:
            return render.NewContest('Success! The new contest ID is: ' + str(info))
        else:
            return render.NewContest('Failed! '+str(info))

class EditContest:
    def GET(self, cid):
        if not db.Contest.IsPrincipal(cid, session.userid) or not db.Contest.Exist(cid):
            raise web.seeother('/')
        (contest, problem) = db.Contest.Get(cid, session.userid, Markdown=False)
        if db.datetime.datetime.now() > contest.ContestEndTime:
            raise web.seeother('/')
        contest['ContestStatus'] = db.Contest.GetStatus(contest.ContestStartTime, contest.ContestEndTime)
        return render.EditContest(cid, contest, problem)
    def POST(self, cid):
        if not db.Contest.IsPrincipal(cid, session.userid):
            raise web.seeother('/')
        (contest, problem) = db.Contest.Get(cid, session.userid, Markdown=False)
        if db.datetime.datetime.now() > contest.ContestEndTime:
            raise web.seeother('/')
        info = {}
        i = web.input(Delete=[],problems=[])
        title = info['ContestTitle'] = i.get('ContestTitle', None)
        stime = info['ContestStartTime'] = i.get('ContestStime', None)
        etime = info['ContestEndTime'] = i.get('ContestEtime', None)
        desc = info['ContestDescription'] = i.get('ContestDescription', None)
        prin = info['ContestPrincipal'] = i.get('ContestPrincipal', None)
        prob = i.get('ProblemList', None)
        delete = i.get('Delete', None)
        porder = i.get('problems', None)
        uprating = i.get('UpRating', 0.0)
        downrating = i.get('DownRating', 0.0)
        mesg = None
        if not title or not vtitle.match(title):
            mesg = 'Contest Title must be between 2 and 50 characters'
        if not desc:
            mesg = 'Contest Description can\'t be empty'
        if not prin:
            mesg = 'There must be one principal'
        else:
            userid = db.Member.GetID(prin)
            if not userid or db.Member.GetLevel(userid) == 0:
                mesg = '[%s] does NOT exist or has no privilege' % prin
        try:
            starttime = time.strptime(stime, '%Y-%m-%d %H:%M:%S')
        except:
            mesg = '[%s] is invalid' % stime
        try:
            endtime = time.strptime(etime, '%Y-%m-%d %H:%M:%S')
        except:
            mesg = '[%s] is invalid' % etime
        ret = {}
        if mesg:
            ret['mesg'] = mesg
            ret['flag'] = False
            return json.dumps(ret)
        ret['mesg'] = 'Edit successfully!\n'+'Time: ' + str(db.Contest.Update(cid, title, stime, etime, desc, userid, prob.strip().split('|'), delete, porder, uprating, downrating)) + 's'
        ret['flag'] = True
        return json.dumps(ret)

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
        (contest, problem) = db.Contest.Get(contestid, session.userid)
        if not contest:
            return render.Contest(None, None)
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
        if contest['ContestStatus'] == 1 and not db.Contest.IsPrincipal(contest.ContestID, session.userid):
            return render.ContestProblem(None, None)
        return render.ContestProblem(contest, problem)

class ContestRank:
    def GET(self, contestid):
        try:
            contestid = int(contestid)
        except:
            contestid = -1
        (contest, problem) = db.Contest.Get(contestid, session.userid)
        if not contest:
            return render.ContestRank(None, None, None)
        if db.Contest.GetStatusByID(contestid) != 3 and not db.Contest.IsPrincipal(contestid,session.userid):
            return render.ContestRank(None, None, None)
        contest['ContestStatus'] = db.Contest.GetStatus(contest.ContestStartTime, contest.ContestEndTime)

        #rank = db.Contest.GetRank(contestid)
        result = db.Contest.GetResult(contestid)
        return render.ContestRank(contest, result, problem)

class WhatsNew:
    def GET(self, arg):
        return render.WhatsNew()

class Upload:
    def GET(self, arg):
        if session.userid == -1:
            raise web.seeother('/')
        return render_plain2.Upload()

    def POST(self, arg):
        if session.userid == -1:
            raise web.seeother('/')
        i = web.input(UploadFile={})
        filedir = '/var/www/vhosts/cofun.org/static/probimg'
        if 'UploadFile' in i and 'Status' in i:
            filepath = i.UploadFile.filename.replace('\\', '/')
            extension = filepath.split('/')[-1].split('.')[-1].lower()
            if extension not in ('jpg', 'png', 'gif'):
                return None
            rand = '%x' % (zlib.crc32(str(random.random())) & 0xffffffff)
            filename = time.strftime('%Y%m%d_%H%M%S_'+rand+'.'+extension)
            fout = open(filedir+'/'+filename, 'wb')
            while True:
                c = i.UploadFile.file.read(BUF_SIZE)
                if c:
                    fout.write(c)
                else:
                    break
            fout.close()
        else:
            return None
        ret = {}
        ret['htm'] = u"""<div class="alert alert-info">
  <button type="button" class="close" data-dismiss="alert">×</button>
  <strong>INFO</strong><p>Done! See <code>/static/probimg/%s</code></p>
</div>"""%filename
        ret['href'] = '/static/probimg/%s' %filename
        web.header("Content-Type","application/json; charset=utf-8")
        return json.dumps(ret)

class UploadData:
    def GET(self, pid, timlim, memlim):
        try:
            pid = int(pid)
        except:
            return "Failed! ProblemID Does Not Exist."
        try:
            timlim = int(timlim)
        except:
            timlim = 1000
        try:
            memlim = int(memlim)
        except:
            memlim = 131072
        global Uploading
        while Uploading:
            time.sleep(0.5)
        Uploading=True
        ret = {}
        (ret['SmartConfig'], ret['DefaultConfig']) = db.Data.Config(pid, timlim, memlim)
        ret['OriginalConfig'] = db.Data.GetConfig(pid)
        Uploading=False
        return json.dumps(ret)
    def POST(self, pid, timlim, memlim):
        if session.userid == -1:
            return "Failed! Please Login First."
        try:
            pid = int(pid)
        except:
            return "Failed! ProblemID Does Not Exist."
        global Uploading
        while Uploading:
            time.sleep(0.5)
        Uploading=True
        pid = str(pid)
        i = web.input(UploadFile={})
        db.Data.Createdir('/home/cofun/data/' + pid + '/')
        filedir = '/home/cofun/data/' + pid
        filename = None
        if 'UploadFile' in i and 'Status' in i:
            filepath = i.UploadFile.filename.replace('\\', '/')
            extension = filepath.split('/')[-1].split('.')[-1].lower()
            if extension not in ('zip'):
                Uploading=False
                return "Failed"
            rand = '%x' % (zlib.crc32(str(random.random())) & 0xffffffff)
            filename = time.strftime('%Y%m%d_%H%M%S_'+rand+'.'+extension)
            db.Data.RemoveFiles(pid)
            fout = open(filedir+'/'+filename, 'wb')
            while True:
                c = i.UploadFile.file.read(BUF_SIZE)
                if c:
                    fout.write(c)
                else:
                    break
            fout.close()
        else:
            Uploading=False
            return "Upload Failed."
        try:
            with contextlib.closing(zipfile.ZipFile(filedir+'/'+filename, 'r')) as z:
                z.extractall(filedir)
        except Exception, e:
            print e
            return "Unzip Failed."
        finally:
            os.remove(filedir+'/'+filename)
            Uploading=False
        ret = {}
        ret['htm'] = db.Data.GetFiles(pid)
        try:
            timlim = int(timlim)
        except:
            timlim = 1000
        try:
            memlim = int(memlim)
        except:
            memlim = 131072
        (ret['SmartConfig'], ret['DefaultConfig']) = db.Data.Config(pid, timlim, memlim)
        ret['OriginalConfig'] = db.Data.GetConfig(pid)
        return json.dumps(ret)
###Series
class NewSeries:
    def GET(self, arg):
        if session.userid == -1 or db.Member.GetLevel(session.userid) < 1:
            raise web.seeother('/')
        return render.NewSeries()
    def POST(self, arg):
        if session.userid == -1 or db.Member.GetLevel(session.userid) < 1:
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
            return render.Series(None, None)
        return render.Series(series, problem)
        
class EditSeries:
    def GET(self, seriesid):
        if db.Member.GetLevel(session.userid) < 1:
            return render.EditSeries(None, None, 'Permission Denied')
        try:
            seriesid = int(seriesid)
        except:
            seriesid = 0
        (series, problem) = db.Series.Get(seriesid, session.userid, Markdown=False)
        return render.EditSeries(series, problem)
    def POST(self, seriesid):
        if db.Member.GetLevel(session.userid) < 1:
            return render.EditSeries(None, None, 'Permission Denied')
        try:
            seriesid = int(seriesid)
        except:
            seriesid = 0
        (series, problem) = db.Series.Get(seriesid, session.userid, Markdown=False)
        i = web.input(Delete=[],problems=[])
        title = i.get('SeriesTitle', None)
        desc = i.get('SeriesDescription', None)
        prob = i.get('ProblemList', None)
        delete = i.get('Delete', None)
        porder = i.get('problems', None)
        mesg = None
        if not title or not vtitle.match(title):
            mesg = 'Series Title must be between 2 and 50 characters'
        if not desc:
            mesg = 'Series Description can\'t be empty'
        ret = {}
        if mesg:
            ret['mesg'] = mesg
            ret['flag'] = False
            return json.dumps(ret)
        res = db.Series.Update(seriesid, prob.strip().split('|'), delete, title, desc, porder)
        ret['mesg'] = 'Edit successfully!\n'+'Time: ' + str(res) + 's'
        ret['flag'] = True
        return json.dumps(ret)
        
class SeriesRank:
    def GET(self, seriesid, page, ajax=None):
        try:
            seriesid = int(seriesid)
        except:
            seriesid = -1
        try:
            page = int(page)
        except:
            page = 1
        (series, problem) = db.Series.Get(seriesid, session.userid)
        if not series:
            return render.SeriesRank(None, None)
        (rank, page, count) = db.Series.GetRank(seriesid, page, CONFIG['seriesrankrows'])
        if ajax:
            return render_plain.SeriesRank(series, page, count, rank, True)
        else:
            return render.SeriesRank(series, page, count, rank)

class AjaxWatchStatus:
    def GET(self, arg):
        i = web.input()
        submits = i.get('submits', '').split('|')
        lst = list()
        for submit in submits:
            try:
                submitid = int(submit)
                lst.append(str(submitid))
            except:
                pass
        lst = db.Status.AjaxWatch(lst) if lst else list()
        for record in lst:
            if record.SubmitStatus > 100:
                record['html'] = RESULTLIST[100] % (record.SubmitStatus-100)
            else:
                record['html'] = RESULTLIST[record.SubmitStatus]
                record['Class'] = ALERTLIST[record.SubmitStatus]
        return json.dumps(lst)

class ContestCurrentRank:
    def GET(self, contestid, page, ajax=None):
        try:
            contestid = int(contestid)
        except:
            contestid = -1
        try:
            page = int(page)
        except:
            page = 1
        (contest, problem) = db.Contest.Get(contestid, session.userid)
        if not contest:
            return render.ContestCurrentRank(None, None, None)
        if db.Contest.GetStatusByID(contestid) != 3 and not db.Contest.IsPrincipal(contestid,session.userid):
            return render.ContestCurrentRank(None, None, None)
        (res, page, count) = db.Contest.GetCurrentRank(contestid, page, CONFIG['contestcurrentrankrows'])
        contest['ContestStatus'] = db.Contest.GetStatus(contest['ContestStartTime'], contest['ContestEndTime'])
        if ajax:
            return render_plain.ContestCurrentRank(contest, page, count, res, problem, True)
        else:
            return render.ContestCurrentRank(contest, page, count, res, problem)

class EditProblem:
    def GET(self, problemid):
        if session.userid == -1 or db.Member.GetLevel(session.userid) < 1:
            raise web.seeother('/')
        try:
            problemid = int(problemid)
        except:
            problemid = 0
        prob = db.Problem.Get(int(problemid), Markdown=False)
        if not prob:
            return render.EditProblem(None)
        if db.Contest.IsProblemNotDone(problemid, 0, session.userid):
            raise web.seeother('/')
        problemid = str(problemid)
        title = prob.ProblemTitle
        time = prob.ProblemTime
        memory = prob.ProblemMemory
        desc = prob.ProblemDescription
        formatin = prob.ProblemInput
        formatout = prob.ProblemOutput
        samplein = prob.ProblemSampleIn
        sampleout = prob.ProblemSampleOut
        hint = prob.ProblemHint
        source = prob.ProblemSource
        spj = prob.SpecialJudge
        code = None
        if spj:
            code = db.Data.GetSpj(problemid)
        datacfg = db.Data.GetConfig(problemid)
        return render.EditProblem(problemid, title, desc, formatin, formatout, samplein, sampleout, time, memory, hint, source, spj, datacfg, code)

    def POST(self, problemid):
        if session.userid == -1 or db.Member.GetLevel(session.userid) < 1:
            raise web.seeother('/')
        try:
            problemid = int(problemid)
        except:
            problemid = 0
        if not db.Problem.Get(int(problemid)):
            return render.EditProblem(None)
        if db.Contest.IsProblemNotDone(problemid, 0, session.userid):
            raise web.seeother('/')
        pid = problemid
        problemid = str(problemid)
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
        spj = i.get('SpecialJudge', None)
        language = int(i.get("SubmitLanguage", None))
        code = i.get("SubmitCode", None)
        datacfg = i.get('DataConfig', None)
        info = ''
        if spj == 'on':
            spj = 1
        else:
            spj = 0
        if not title or not vtitle.match(title):
            return render.EditProblem(problemid, title, desc, formatin, formatout, samplein, sampleout, time, memory, hint, source, spj, datacfg, code, 'Title must be between 2 to 100 characters.')
        if not time or not vtime.match(time):
            return render.EditProblem(problemid, title, desc, formatin, formatout, samplein, sampleout, time, memory, hint, source, spj, datacfg, code, 'Time Limit must be between 100 and 999999.')
        if not memory or not vmemory.match(time):
            return render.EditProblem(problemid, title, desc, formatin, formatout, samplein, sampleout, time, memory, hint, source, spj, datacfg, code, 'Memory Limit must be between 100 and 999999.')
        if not formatin:
            return render.EditProblem(problemid, title, desc, formatin, formatout, samplein, sampleout, time, memory, hint, source, spj, datacfg, code, 'Must have Input Format.')
        if not formatout:
            return render.EditProblem(problemid, title, desc, formatin, formatout, samplein, sampleout, time, memory, hint, source, spj, datacfg, code, 'Must have Output Format.')
        if not samplein:
            return render.EditProblem(problemid, title, desc, formatin, formatout, samplein, sampleout, time, memory, hint, source, spj, datacfg, code, 'Must have sample input.')
        if not sampleout:
            return render.EditProblem(problemid, title, desc, formatin, formatout, samplein, sampleout, time, memory, hint, source, spj, datacfg, code, 'Must have sample output.')
        if not datacfg:
            return render.EditProblem(problemid, title, desc, formatin, formatout, samplein, sampleout, time, memory, hint, source, spj, datacfg, code, 'Must have Data Config.')
        if not code and spj:
            return render.EditProblem(problemid, title, desc, formatin, formatout, samplein, sampleout, time, memory, hint, source, spj, datacfg, code, 'Spj code can\'t be empty.')
        if spj:
            for i in xrange(1,4):
                if i != language and os.path.exists(SPJFILE[i] % pid):
                    os.remove(SPJFILE[i] % pid)
            if os.path.exists(SPJ % pid):
                os.remove(SPJ % pid)
            try:
                with open(SPJFILE[language] % pid, 'w') as f:
                    f.write(code)
                os.system(COMPILE_COMMAND[language] % (pid, pid) + COMPILE_REWRITE % pid)
                info = open(COMPILE_INFO % pid, 'r').read().replace(DATA_DIR % pid,'')
            except Exception, e:
                print e
            if not os.path.exists(SPJ % pid):
                return render.EditProblem(problemid, title, desc, formatin, formatout, samplein, sampleout, time, memory, hint, source, spj, datacfg, code, 'Failed! Spj code compile error.', info)
        db.Problem.Edit(int(problemid), title, desc, formatin, formatout, samplein, sampleout, time, memory, hint, source, spj, datacfg)
        return render.EditProblem(problemid, title, desc, formatin, formatout, samplein, sampleout, time, memory, hint, source, spj, datacfg, code, 'Edit successfully!', info)

class FAQ:
    def GET(self, arg):
        return render.FAQ()
if __name__ == '__main__':
    app.run()
