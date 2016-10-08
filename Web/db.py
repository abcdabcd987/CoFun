import web
import time
import cgi
import os
import hashlib
import datetime
import markdown2
from config import CONFIG
from config import SPJFILE

db = web.database(dbn=CONFIG['dbtype'], user=CONFIG['dbuser'], pw=CONFIG['dbpasswd'], db=CONFIG['dbname'])

class Utility(object):
    @staticmethod
    def SHA1(content):
        return hashlib.sha1(content).hexdigest()

    @staticmethod
    def MD5(content):
        return hashlib.md5(content).hexdigest()

class Member(object):
    @staticmethod
    def GetLevel(userid):
        res = list(db.select("Privilege", what="Level", where="UserID="+str(userid)))
        if len(res) == 0:
            return 0
        return res[0]['Level']
    
    @staticmethod
    def GetID(nameoremail, uid=-1):
        res = list(db.select("User", what="UserID", where="UserEmail='"+nameoremail+"' or UserName='"+nameoremail+"'"))
        return None if len(res) == 0 or int(res[0]['UserID']) == uid else int(res[0]['UserID'])
    
    @staticmethod
    def GetRanklist(offset, limit, order=None):
        if not order:
            order = '-Rating, -Solved, Submit, UserID'
        res = list(db.select("User", offset=offset, limit=limit, order=order))
        return res
    
    @staticmethod
    def GetChanges(userid):
        user = Member.GetInfo(userid)
        if not user:
            return None
        changes = db.select("RatingChanges", what="*", where="UserID="+str(userid), order="EndTime desc")
        if changes:
            changes = list(changes)
        else:
            return None
        for change in changes:
            (change.year, change.month, change.day) = map(int,change.EndTime.strftime('%Y,%m,%d').split(','))
            change.month -= 1
            change.sRatingDelta = str(change.RatingDelta)
        return changes
		
    @staticmethod
    def GetDetail(userid):
        user = Member.GetInfo(userid)
        if not user:
            return (None, None)
        done = db.select("Submit", what="DISTINCT ProblemID", where="UserID="+str(userid)+" AND SubmitStatus = 3", order="ProblemID")
        if done:
            done = list(done)
        else:
            done = list()
        #user.Signature = None
        donelist = []
        for i in done:
            if not Contest.IsProblemNotDone(i.ProblemID, 0):
                donelist.append(str(i.ProblemID))
        #user.Solved = len(donelist)
        if user.Submit:
            user.Ratio = ("%.1f" % float(user.Solved * 100.0 / user.Submit))
        else:
            user.Ratio = 0.0
        # (SELECT if(isnull(Solved/Submit),0,Solved/Submit))>%s)
        user.Rank = list(db.select("User", what="count(*)", where="Rating>%d OR Rating=%d AND (Solved>%d OR Solved=%d AND Submit<%d)" % (user.Rating, user.Rating, user.Solved, user.Solved, user.Submit)))[0]['count(*)'] + 1
        user._Rank = list(db.select("User", what="count(*)", where="Rating>%d OR Rating=%d AND (Solved>%d OR Solved=%d AND Submit<%d OR (Submit=%d AND UserID<%d))" % (user.Rating, user.Rating, user.Solved, user.Solved, user.Submit, user.Submit, user.UserID)))[0]['count(*)'] + 1
        #user.Submit = Status.Count(UserName=user.UserName)
        #print user.Rank
        if len(donelist):
            all = db.select("Submit", what="count(*), ProblemID", where="UserID="+str(userid)+" AND ProblemID IN ("+','.join(donelist)+")", group="ProblemID", order="ProblemID")
        else:
            all = []
        if len(donelist):
            problems = list(db.select("Problem", where="ProblemID IN ("+','.join(donelist)+")", order="ProblemID"))
        else:
            problems = list()
        for i in problems:
            if not i.Submit:
                i.Submit = 0
            if not i.Solved:
                i.Solved = 0
            if i.Submit == 0:
                i.Ratio = 0.0
            else:
                i.Ratio = ("%.1f" % float(i.Solved * 100.0 / i.Submit))
            for j in all:
                if i.ProblemID != j.ProblemID:
                    print 'error'
                i.UserSubmit = j['count(*)']
                #if i.ProblemID == 1122:
                #    user.Solved -= 1
                #    user.Submit -= j['count(*)']
                break
        #db.update("User", Solved=user.Solved, Submit=user.Submit, where='UserID='+str(userid))
        return (user, problems)

    #@staticmethod
    #def GetPassword(userid):
    #    res = list(db.select("User", what="UserPassword", where="UserID="+str(userid)))
    #    return None if len(res) == 0 else res[0]['UserPassword']

    @staticmethod
    def GetInfo(userid):
        res = list(db.select("User", where="UserID="+str(userid)))
        res = None if len(res) == 0 else res[0]
        #if res:
            #res.UserName = cgi.escape(res.UserName).replace(' ','&nbsp;')
            #res.UserName = '<a>'+res.UserName+'</a>'
            #res.UserName = 
        return res

    @staticmethod
    def GetIDByRank(rank):
        if rank == 0:
            return 0
        order = '-Rating, -Solved, Submit, UserID'
        res = db.select("User", what='UserID', offset=rank-1, limit=1, order=order)
        if not res:
            return 0
        #if res:
            #res.UserName = cgi.escape(res.UserName).replace(' ','&nbsp;')
            #res.UserName = '<a>'+res.UserName+'</a>'
            #res.UserName = 
        return list(res)[0].UserID

    @staticmethod
    def Add(username, userpwd, useremail, realname, signature):
        if Member.GetID(username) or Member.GetID(useremail):
            return None
        else:
            return db.insert("User", UserName=username, UserEmail=useremail, RealName=realname, UserPassword=Utility.SHA1(userpwd), Signature=signature)

    @staticmethod
    def Modify(uid, username, userpwd, realname, signature):
        if Member.GetID(username, uid):
            return None
        else:
            db.update("User", UserName=username, RealName=realname, UserPassword=Utility.SHA1(userpwd), Signature=signature, where='UserID='+str(uid))
            #db.update("User",Signature="",RealName="再乱改就真封了",where="UserID=44")
            return uid

    @staticmethod
    def GetLastLanguage(userid):
        res = list(db.select("Submit", what="SubmitLanguage", limit=1, where="UserID="+str(userid), order="SubmitID DESC"))
        return res[0]['SubmitLanguage'] if res else None

    @staticmethod
    def Count():
        res = list(db.select("User", what="count(*)"))[0]['count(*)']
        return res

class Problem(object):
    @staticmethod
    def NewID():
        return (list(db.select("information_schema.tables", what="AUTO_INCREMENT", where="table_schema = 'cofun' AND table_name = 'Problem'")))[0]['AUTO_INCREMENT']
    @staticmethod
    def Add(title, desc, fin, fout, sin, sout, time, memory, hint, source, spj):
        #Data.WriteConfig(Problem.NewID(), datacfg)
        return db.insert("Problem", ProblemTitle=title, ProblemDescription=desc, ProblemInput=fin, ProblemOutput=fout, ProblemSampleIn=sin, ProblemSampleOut=sout, ProblemTime=time, ProblemMemory=memory, ProblemHint=hint, ProblemSource=source, SpecialJudge=spj, Submit=0, Solved=0)

    @staticmethod
    def Edit(probid, title, desc, fin, fout, sin, sout, time, memory, hint, source, spj, datacfg):
        Data.WriteConfig(probid, datacfg)
        return db.update("Problem", ProblemTitle=title, ProblemDescription=desc, ProblemInput=fin, ProblemOutput=fout, ProblemSampleIn=sin, ProblemSampleOut=sout, ProblemTime=time, ProblemMemory=memory, ProblemHint=hint, ProblemSource=source, SpecialJudge=spj, where="ProblemID="+str(probid))

    @staticmethod
    def GetList(offset, limit, userid):
        res = list(db.select("Problem", what="ProblemID, ProblemTitle, ProblemSource, Submit, Solved", offset=offset, limit=limit, order="ProblemID"))
        if not res:
            return None
        if userid == -1:
            done = list()
        else:
            done = db.select("Submit", what="DISTINCT ProblemID, SubmitStatus", where="UserID="+str(userid)+" AND SubmitStatus IN (3, 4) AND Submit.ProblemID IN ( SELECT * FROM (SELECT ProblemID FROM Problem LIMIT "+str(offset)+","+str(limit)+") AS tmp1)", order="ProblemID")
            if done:
                done = list(done)
            else:
                done = list()
        res = filter(lambda x:not Contest.IsProblemNotDone(x.ProblemID, 0, userid), res)
        for i in res:
            #i.Submit = Status.Count(ProblemID=i.ProblemID)
            #i.Solved = Status.Count(ProblemID=i.ProblemID, SubmitStatus=3, Group='User.UserID')
            if not i.Submit:
                i.Submit = 0
            if not i.Solved:
                i.Solved = 0
            if i.Submit == 0:
                i.Ratio = 0.0
            else:
                i.Ratio = ("%.1f" % float(i.Solved * 100.0 / i.Submit))
            #db.update("Problem", Solved=i.Solved, Submit=i.Submit, where="ProblemID="+str(i.ProblemID))
            i.ProblemDone = 0
            for j in done:
                if i.ProblemID == j.ProblemID:
                    if j.SubmitStatus == 3:
                        i.ProblemDone = 1
                        break
                    else:
                        i.ProblemDone = 2
        return res

#SELECT DISTINCT ProblemID, SubmitStatus FROM Submit 
#WHERE UserID=%s AND SubmitStatus IN (3, 4) AND Submit.ProblemID IN 
#(
#  SELECT * FROM (SELECT ProblemID FROM Problem LIMIT %s,%s) AS tmp1
#) ORDER BY ProblemID

    @staticmethod
    def Get(problemid, Markdown=True):
        res = db.select("Problem", where="ProblemID="+str(problemid))
        if not res:
            return None
        res = list(res)[0]
        if not res.Submit:
            res.Submit = 0
        if not res.Solved:
            res.Solved = 0
        #res.Submit = Status.Count(ProblemID=problemid)
        #res.Solved = Status.Count(ProblemID=problemid, SubmitStatus=3, Group='User.UserID')
        if Markdown:
            res.ProblemDescription = markdown2.markdown(res.ProblemDescription)
            res.ProblemInput = markdown2.markdown(res.ProblemInput)
            res.ProblemOutput = markdown2.markdown(res.ProblemOutput)
            res.ProblemHint = markdown2.markdown(res.ProblemHint)
        return res

    @staticmethod
    def Count():
        return int(list(db.select("Problem", what="count(*)"))[0]["count(*)"])

    @staticmethod
    def Exist(problemid):
        try:
            problemid = int(problemid)
        except:
            problemid = 0
        res = list(db.select("Problem", what="count(*)", where="ProblemID="+str(problemid)))
        res = res[0]['count(*)']
        return True if res else False

class Status(object):
    @staticmethod
    def Submit(problemid, contestid, userid, lang, code, prin):
        Rating = Member.GetInfo(userid).Rating
        return db.insert("Submit", Rating=Rating, ProblemID=problemid, ContestID=contestid, UserID=userid, SubmitLanguage=lang, SubmitCode=code, CodeLength=len(code), ContestPrincipal=prin)

    @staticmethod
    def Count(ProblemID='', UserName='', SubmitLanguage='', SubmitStatus='', ContestID='', Group=None, Prin=0):
        where = 'User.UserID=Submit.UserID'
        if ProblemID:
            where += ' AND ProblemID='+str(ProblemID)
        if UserName:
            where += " AND User.UserName='"+str(UserName)+"'"
        if SubmitLanguage:
            where += ' AND SubmitLanguage='+str(SubmitLanguage)
        if SubmitStatus:
            where += ' AND SubmitStatus='+str(SubmitStatus)
            if Prin != 0:
                where += ' AND (ContestPrincipal=%s OR ContestPrincipal=0)' % Prin
            else:
                where += ' AND ContestPrincipal=0'
        if ContestID:
            where += ' AND ContestID='+str(ContestID)
        if not Group:
            return int(list(db.select("Submit, User", what="count(*)", where=where))[0]['count(*)'])
        else:
            return len(list(db.select("Submit, User", what="User.UserID", where=where, group=Group)))

    @staticmethod
    def GetList(offset, limit, ProblemID='', UserName='', SubmitLanguage='', SubmitStatus='', ContestID='', Prin=0):
        where = 'User.UserID=Submit.UserID'
        if ProblemID:
            where += ' AND ProblemID='+str(ProblemID)
        if UserName:
            where += " AND User.UserName='"+str(UserName)+"'"
        if SubmitLanguage:
            where += ' AND SubmitLanguage='+str(SubmitLanguage)
        if SubmitStatus:
            where += ' AND SubmitStatus='+str(SubmitStatus)
            if Prin != 0:
                where += ' AND (ContestPrincipal=%s OR ContestPrincipal=0)' % Prin
            else:
                where += ' AND ContestPrincipal=0'
        if ContestID:
            where += ' AND ContestID='+str(ContestID)

        res = list(db.select("Submit, User", what="SubmitID, Submit.UserID, User.UserName, ProblemID, ContestID, SubmitStatus, SubmitScore, SubmitRunMemory, SubmitRunTime, SubmitLanguage, CodeLength, SubmitTime, Submit.Rating", where=where, order="SubmitID DESC", offset=offset, limit=limit))
        if res:
            for submit in res:
                submit.SubmitScore = "%3.1f" % float(submit.SubmitScore)
        return None if len(res) == 0 else res

    @staticmethod
    def Detail(submitid):
        res1 = list(db.select("Result", what="Result, RunTime, RunMemory, Score, Diff", where="SubmitID="+str(submitid)));
        res2 = list(db.select("Submit, User", where="User.UserID = Submit.UserID AND SubmitID="+str(submitid)));
        if res2:
            res2 = res2[0]
            res2.SubmitScore = '%3d' % res2.SubmitScore
            for testcase in res1:
                testcase.Score = '%3d' % testcase.Score
        return (None, None) if not res2 else (res1, res2)

    @staticmethod
    def AjaxWatch(submits):
        res = list(db.select("Submit", what="SubmitID, SubmitRunTime, SubmitRunMemory, SubmitStatus, SubmitScore", where="SubmitID IN ("+','.join(submits)+")"))
        if res:
            for submit in res:
                submit.SubmitScore = "%3.1f" % float(submit.SubmitScore)
        return None if len(res) == 0 else res

class Contest(object):
    @staticmethod
    def Add(title, stime, etime, desc, prin, probs, uprating, downrating):
        for prob in probs:
            if Contest.IsProblemNotDone(prob, 0, prin):
                return (False, 'Problem '+str(prob)+' Locked')
            if not Problem.Exist(prob):
                return (False, 'Problem '+str(prob)+' Does Not Exist')
        cid = db.insert("Contest", ContestTitle=title, ContestStartTime=stime, ContestEndTime=etime, ContestDescription=desc, ContestPrincipal=prin, UpRating=uprating, DownRating=downrating)
        for idx,p in enumerate(probs):
            db.insert("ContestProblem", ContestID=cid, ProblemID=p, ProblemOrder=idx)
        return (True, cid)
    
    @staticmethod
    def Update(cid, title, stime, etime, desc, prin, probs, delete, porder, uprating, downrating):
        st = time.time()
        idx = 0
        for p in porder:
            p = p.split('p')[1].rstrip('#')
            if Problem.Exist(p):
                idx += 1
                db.update("ContestProblem", where="ContestID="+str(cid)+" AND ProblemID="+str(p), ProblemOrder=idx)
        idx = (list(db.select("ContestProblem", what="count(*)", where="ContestID="+str(cid))))[0]["count(*)"]
        for p in probs:
            if Problem.Exist(p) and not Contest.IsProblemNotDone(p, 0, prin) and (list(db.select("ContestProblem", what="count(*)", where="ContestID="+str(cid)+" AND ProblemID="+str(p))))[0]["count(*)"] == 0:
                idx += 1
                db.insert("ContestProblem", ContestID=cid, ProblemID=p, ProblemOrder=idx)
        if delete:
            for prob in delete:
                try:
                    p = int(prob)
                except:
                    p = 0
                if p >= 1000:
                    db.delete("ContestProblem", where="ProblemID="+str(p)+" AND ContestID="+str(cid))
        db.update("Contest", ContestTitle=title, ContestStartTime=stime, ContestEndTime=etime, ContestDescription=desc, ContestPrincipal=prin, UpRating=uprating, DownRating=downrating, where="ContestID="+str(cid))
        return time.time() - st

    @staticmethod
    def Get(cid, userid, Markdown=True):
        contest = db.select("Contest, User", what="UpRating, DownRating, ContestID, ContestTitle, ContestStartTime, ContestEndTime, ContestDescription, UserName AS ContestPrincipal, ContestPrincipal AS Principal", where="User.UserID=Contest.ContestPrincipal AND ContestID="+str(cid))
        prob = db.select("ContestProblem, Problem", what="Problem.ProblemID, Problem.ProblemSource, Problem.ProblemTitle", where="ContestProblem.ContestID="+str(cid)+" AND Problem.ProblemID=ContestProblem.ProblemID", order="ContestProblem.ProblemOrder")
        if not contest:
            return (None, None)
        contest = list(contest)[0]
        if not prob:
            prob = list()
        else:
            prob = list(prob)
        status = Contest.GetStatus(contest.ContestStartTime, contest.ContestEndTime)
        if userid == -1:
            done = list()
        else:
            if status == 3 or Contest.IsPrincipal(cid,userid):
                done = db.select("Submit", what="DISTINCT ProblemID, SubmitStatus", where="UserID="+str(userid)+" AND SubmitStatus IN (3, 4) AND Submit.ProblemID IN (SELECT ProblemID FROM ContestProblem WHERE ContestID="+str(cid)+")", order="ProblemID")
            else:
                done = db.select("Submit", what="DISTINCT ProblemID", where="UserID="+str(userid)+" AND ContestID="+str(cid), order="ProblemID")
            done = list(done) if done else list()
        if status == 3 or Contest.IsPrincipal(cid,userid):
            for i in prob:
                i['ProblemDone'] = 0
                for j in done:
                    if i.ProblemID == j.ProblemID:
                        if j.SubmitStatus == 3:
                            i.ProblemDone = 1
                            break
                        else:
                            i.ProblemDone = 2
        else:
            for i in prob:
                i['ProblemDone'] = 0
                for j in done:
                    if i.ProblemID == j.ProblemID:
                        i.ProblemDone = 3
                        break
#SELECT DISTINCT ProblemID, SubmitStatus FROM Submit 
#WHERE UserID=%s AND SubmitStatus IN (3, 4) AND Submit.ProblemID IN 
#(
#  SELECT ProblemID FROM ContestProblem WHERE ContestID=%s
#) ORDER BY ProblemID
        if Markdown:
            contest.ContestDescription = markdown2.markdown(contest.ContestDescription)
        contest.FullScore = list(db.select("ContestProblem", what="COUNT(*) AS Count", where="ContestID="+str(cid)))[0]['Count']*100.0
        return (contest, prob)

    @staticmethod
    def GetCurrentRank(cid, page, count):
        table = db.select('( SELECT ProblemId, SubmitScore, SubmitRunTime, UserID FROM ( SELECT ProblemID, UserID, SubmitScore, SubmitRunTime FROM Submit WHERE ContestPrincipal=0 AND ProblemID IN ( SELECT ProblemID FROM ContestProblem WHERE ContestID='+str(cid)+') ORDER BY SubmitID DESC) AS tmp1 GROUP BY UserID, ProblemID) AS tmp2, User', 
                what="tmp2.UserID, UserName, RealName, ProblemID, SubmitScore, SubmitRunTime, User.Rating", 
                where="User.UserID=tmp2.UserID")
        cp = db.select("ContestProblem", what="ProblemID", where="ContestID="+str(cid))
        exist = {}
        for i in cp:
            exist[i.ProblemID] = True
        #SELECT tmp2.UserID, UserName, ProblemID, SubmitScore, SubmitRunTime, User.Rating FROM
        #(
        #  SELECT ProblemId, SubmitScore, UserID FROM
        #  (
        #    SELECT ProblemID, UserID, SubmitScore FROM Submit WHERE ContestPrincipal=0 AND ProblemID IN 
        #    (
        #      SELECT ProblemID FROM ContestProblem WHERE ContestID=cid
        #    ) ORDER BY SubmitID DESC
        #  ) AS tmp1 GROUP BY ProblemID, UserID
        #) AS tmp2, User WHERE User.UserID=tmp2.UserID;
        
        if not table :
            return None
        table = list(table)
        res = list()
        lastname = None
        for i in table:
            if not exist.get(i.ProblemID, False):
                continue
            if lastname != i['UserName']:
                lastname = i['UserName']
                res.append({'UserName':lastname, 'Score':0, 'UserID':i['UserID'], 'Time':0, 'RealName':i['RealName'], 'Rating':i['Rating']})
            res[-1][i['ProblemID']] = i['SubmitScore']
            res[-1]['Score'] += i['SubmitScore']
            res[-1]['Time'] += i['SubmitRunTime']
        res = sorted(res,key = lambda x:(-x['Score'],x['Time']))
        totpage = len(res)//count + 1
        page = min(page, totpage)
        page = max(1, page)
        return (res[(page - 1) * count:min(len(res), page * count)], page, totpage)

    @staticmethod
    def GetProblem(cid, pid):
        contest = db.select("Contest", where="ContestID="+str(cid))
        prob = db.select("ContestProblem, Problem", what="Problem.*", where="ContestProblem.ContestID="+str(cid)+" AND Problem.ProblemID=ContestProblem.ProblemID AND Problem.ProblemID="+str(pid))
        if not contest or not prob:
            return (None, None)
        else:
            contest = list(contest)[0]
            contest.ContestDescription = markdown2.markdown(contest.ContestDescription)
            prob = list(prob)[0]
            prob.ProblemDescription = markdown2.markdown(prob.ProblemDescription)
            prob.ProblemInput = markdown2.markdown(prob.ProblemInput)
            prob.ProblemOutput = markdown2.markdown(prob.ProblemOutput)
            prob.ProblemHint = markdown2.markdown(prob.ProblemHint)
            return (contest, prob)

    @staticmethod
    def GetList(offset, limit):
        res = list(db.select("Contest", offset=offset, limit=limit, order="ContestID DESC"))
        return None if len(res) == 0 else res

    @staticmethod
    def Count():
        return int(list(db.select("Contest", what="count(*)"))[0]["count(*)"])

    @staticmethod
    def Exist(cid):
        return True if int(list(db.select("Contest", what="count(*)", where="ContestID="+str(cid)))[0]["count(*)"]) else False

    @staticmethod
    def GetStatus(stime, etime):
        now = datetime.datetime.now()
        if stime > now:
            return 1
        elif stime <= now <= etime:
            return 2
        else:
            return 3

    @staticmethod
    def GetStatusByID(cid):
        contest = db.select("Contest", where="ContestID="+str(cid))
        if not contest:
            return 3
        contest = list(contest)[0]
        return Contest.GetStatus(contest.ContestStartTime, contest.ContestEndTime)

    @staticmethod
    def GetPrincipal(cid):
        contest = db.select("Contest", where="ContestID="+str(cid))
        if not contest:
            return 0
        contest = list(contest)[0]
        return contest.ContestPrincipal
        
    @staticmethod
    def IsPrincipal(cid,uid):
        return Contest.GetPrincipal(cid) == uid or Member.GetLevel(uid) >= 10

    @staticmethod
    def IsProblemNotDone(pid, cid=0, uid=-1):
        try:
            pid = int(pid)
        except:
            return False
        contests = list(db.select("ContestProblem", where="ProblemID="+str(pid)))
        if not contests:
            return False
        for contest in contests:
            if contest.ContestID == cid:
                return False
        for contest in contests:
            if Contest.GetStatusByID(contest.ContestID) != 3 and not Contest.IsPrincipal(contest.ContestID,uid):
                return True
        return False

    @staticmethod
    def GetResult(cid):
        table = db.select('(SELECT * FROM (SELECT UserID, ProblemID, SubmitScore, SubmitRunTime, Rating FROM Submit WHERE ContestID='+str(cid)+' ORDER BY SubmitID DESC) as tmp1 GROUP BY UserID, ProblemID) as tmp2, User', 
                what='tmp2.UserID, UserName, RealName, ProblemID, SubmitScore, SubmitRunTime, tmp2.Rating', where='tmp2.UserID=User.UserID')
        cp = db.select("ContestProblem", what="ProblemID", where="ContestID="+str(cid))
        exist = {}
        for i in cp:
            exist[i.ProblemID] = True
        #SELECT tmp2.UserID, UserName, ProblemID, SubmitScore, SubmitRunTime, tmp2.Rating FROM
        #(
        #  SELECT *
        #  FROM 
        #  (
        #    SELECT UserID, ProblemID, SubmitScore, SubmitRunTime, Rating FROM Submit WHERE ContestID=1000 ORDER BY SubmitID DESC
        #  ) as tmp1
        #  GROUP BY UserID, ProblemID
        #) as tmp2, User
        #WHERE tmp2.UserID=User.UserID
        
        if not table :
            return None
        table = list(table)
        res = list()
        lastname = None

        for i in table:
            if not exist.get(i.ProblemID, False):
                continue
            if lastname != i['UserName']:
                lastname = i['UserName']
                res.append({'UserName':lastname, 'Score':0, 'UserID':i['UserID'], 'Time':0, 'RealName':i['RealName'], 'Rating':i['Rating']})
            res[-1][i['ProblemID']] = i['SubmitScore']
            res[-1]['Score'] += i['SubmitScore']
            res[-1]['Time'] += i['SubmitRunTime']
        res = sorted(res,key = lambda x:(-x['Score'],x['Time']))
        return res

    @staticmethod
    def GetRank(cid):#Not used
        res = db.select('(SELECT * FROM (SELECT UserID, ProblemID, SubmitScore, SubmitRunTime FROM Submit WHERE ContestID='+str(cid)+' ORDER BY SubmitID DESC) as tmp1 GROUP BY UserID, ProblemID) as tmp2, User', 
                what='tmp2.UserID, UserName, SUM(SubmitScore) AS Score, SUM(SubmitRunTime) AS Time', where='tmp2.UserID=User.UserID', group='UserID', order='Score DESC, Time ASC')
        return list(res) if res else None
        #SELECT tmp2.UserID, UserName, SUM(SubmitScore) AS Score, SUM(SubmitRunTime) AS Time FROM
        #(
        #  SELECT *
        #  FROM 
        #  (
        #    SELECT UserID, ProblemID, SubmitScore, SubmitRunTime FROM Submit WHERE ContestID=1000 ORDER BY SubmitID DESC
        #  ) as tmp1
        #  GROUP BY UserID, ProblemID
        #) as tmp2, User
        #WHERE tmp2.UserID=User.UserID GROUP BY UserID ORDER BY Score DESC

class Series(object):
    @staticmethod
    def Add(title, desc, probs):
        cid = db.insert("Series", SeriesTitle=title, SeriesDescription=desc)
        idx = (list(db.select("SeriesProblem", what="count(*)", where="SeriesID="+str(cid))))[0]["count(*)"]
        for p in probs:
            if Problem.Exist(p) and not Contest.IsProblemNotDone(p) and (list(db.select("SeriesProblem", what="count(*)", where="SeriesID="+str(cid)+" AND ProblemID="+str(p))))[0]["count(*)"] == 0:
                idx += 1
                db.insert("SeriesProblem", SeriesID=cid, ProblemID=p, ProblemOrder=idx)
        return cid
        
    @staticmethod
    def Update(cid, probs, delete, title, desc, porder):
        st = time.time()
        idx = 0
        for p in porder:
            if Problem.Exist(p):
                idx += 1
                db.update("SeriesProblem", where="SeriesID="+str(cid)+" AND ProblemID="+str(p), ProblemOrder=idx)
        idx = (list(db.select("SeriesProblem", what="count(*)", where="SeriesID="+str(cid))))[0]["count(*)"]
        for p in probs:
            if Problem.Exist(p) and not Contest.IsProblemNotDone(p) and (list(db.select("SeriesProblem", what="count(*)", where="SeriesID="+str(cid)+" AND ProblemID="+str(p))))[0]["count(*)"] == 0:
                idx += 1
                db.insert("SeriesProblem", SeriesID=cid, ProblemID=p, ProblemOrder=idx)
        if delete:
            for prob in delete:
                try:
                    p = int(prob)
                except:
                    p = 0
                if p >= 1000:
                    db.delete("SeriesProblem", where="ProblemID="+str(p)+" AND SeriesID="+str(cid))
        db.update("Series", where="SeriesID="+str(cid), SeriesTitle=title, SeriesDescription=desc)
        return time.time() - st

    @staticmethod
    def Get(cid, userid, Markdown=True):
        series = db.select("Series", where="SeriesID="+str(cid))
        prob = db.select("SeriesProblem, Problem", what="Problem.ProblemID, Problem.ProblemSource, Problem.ProblemTitle, Problem.Submit, Problem.Solved", where="SeriesProblem.SeriesID="+str(cid)+" AND Problem.ProblemID=SeriesProblem.ProblemID", order="SeriesProblem.ProblemOrder")
        if not series:
            return (None, None)
        if not prob:
            prob = list()
        else:
            prob = list(prob)
        if userid == -1:
            done = list()
        else:
            done = db.select("Submit", what="DISTINCT ProblemID, SubmitStatus", where="UserID="+str(userid)+" AND SubmitStatus IN (3, 4) AND Submit.ProblemID IN (SELECT ProblemID FROM SeriesProblem WHERE SeriesID="+str(cid)+")", order="ProblemID")
            done = list(done) if done else list()
        prob = filter(lambda x:not Contest.IsProblemNotDone(x.ProblemID, 0, userid), prob)
        for i in prob:
            if not i.Submit:
                i.Submit = 0
            if not i.Solved:
                i.Solved = 0
            if i.Submit != 0:
                i['Ratio'] = "%.1f" % float(i.Solved * 100.0 / i.Submit)
            else:
                i['Ratio'] = 0.0
            i['ProblemDone'] = 0
            for j in done:
                if i.ProblemID == j.ProblemID:
                    if j.SubmitStatus == 3:
                        i.ProblemDone = 1
                        break
                    else:
                        i.ProblemDone = 2
#SELECT DISTINCT ProblemID, SubmitStatus FROM Submit 
#WHERE UserID=%s AND SubmitStatus IN (3, 4) AND Submit.ProblemID IN 
#(
#  SELECT ProblemID FROM SeriesProblem WHERE SeriesID=%s
#) ORDER BY ProblemID
        series = list(series)[0]
        if Markdown:
            series.SeriesDescription = markdown2.markdown(series.SeriesDescription)
        series.FullScore = list(db.select("SeriesProblem", what="COUNT(*) AS Count", where="SeriesID="+str(cid)))[0]['Count']*100.0
        return (series, prob)

    @staticmethod
    def GetList(offset, limit):
        res = list(db.select("Series", offset=offset, limit=limit, order="SeriesID DESC"))
        return None if len(res) == 0 else res

    @staticmethod
    def Count():
        return int(list(db.select("Series", what="count(*)"))[0]["count(*)"])

    @staticmethod
    def GetRank(sid, page, count):
        res = db.select('( SELECT ProblemId, SubmitScore, SubmitRunTime, UserID FROM ( SELECT ProblemID, UserID, SubmitScore, SubmitRunTime FROM Submit WHERE Submit.ContestPrincipal=0 AND ProblemID IN ( SELECT ProblemID FROM SeriesProblem WHERE SeriesID='+str(sid)+') ORDER BY SubmitID DESC) AS tmp1 GROUP BY ProblemID, UserID) AS tmp2, User', 
                what="tmp2.UserID, UserName, RealName, SUM(SubmitScore) AS Score, SUM(SubmitRunTime) AS Time, User.Rating", 
                group='UserID', order='Score DESC, Time ASC', where="User.UserID=tmp2.UserID")
        if res:
            res = list(res)
        else:
            res = list()
        totpage = len(res)//count + 1
        page = min(page, totpage)
        page = max(1, page)
        return (res[(page - 1) * count:min(len(res), page * count)], page, totpage)

        #SELECT tmp2.UserID, UserName, SUM(SubmitScore) AS Score, User.Rating FROM
        #(
        #  SELECT ProblemId, SubmitScore, UserID FROM
        #  (
        #    SELECT ProblemID, UserID, SubmitScore FROM Submit WHERE Submit.ContestPrincipal=0 AND ProblemID IN 
        #    (
        #      SELECT ProblemID FROM SeriesProblem WHERE SeriesID=sid
        #    ) ORDER BY SubmitID DESC
        #  ) AS tmp1 GROUP BY ProblemID, UserID
        #) AS tmp2, User WHERE User.UserID=tmp2.UserID GROUP BY UserID ORDER BY Score DESC ;

class Data(object):
    @staticmethod
    def isdatafile(name):
        name = str(name)
        return (name != 'data.config' and name != 'spj' and name.split('.')[-1] not in ('pas', 'cc', 'cpp', 'c'))
        
    @staticmethod
    def longestCommonPrefix(strs):
        if strs is None or strs ==[]:return ''
        result =''
        pre =None
        for cur in xrange(len(strs[0])):
            for node in strs:
                if len(node) <=cur:
                    return result
                if pre is not None:
                    if pre != node[cur]:
                        return result
                pre =node[cur]
            result+=pre
            pre=None
        
        return result

    @staticmethod
    def Createdir(s):
        if not os.path.isdir(s):
            os.mkdir(s)
    @staticmethod
    def RemoveFiles(pid):
        Data.Createdir('/home/cofun/data/'+str(pid)+'/')
        for root, dirs, files in os.walk('/home/cofun/data/'+str(pid), topdown=False):
            for name in files:
                if Data.isdatafile(name) or root != '/home/cofun/data/'+str(pid):
                    os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        
    @staticmethod
    def GetFiles(pid):
        Data.Createdir('/home/cofun/data/'+str(pid)+'/')
        res = ""
        cnt = 0
        for root, dirs, files in os.walk('/home/cofun/data/'+str(pid), topdown=False):
            for name in files:
                cnt += 1
                res += '#' + str(cnt) + ':  ' + os.path.join(root, name).replace('/home/cofun/data/'+str(pid)+'/', '', 1) + '\n'
            for name in dirs:
                cnt += 1
                res += '#' + str(cnt) + ':  ' + os.path.join(root, name).replace('/home/cofun/data/'+str(pid)+'/', '', 1) + '\n'
        return res
        
    @staticmethod
    def WriteConfig(pid, dataconfig):
        Data.Createdir('/home/cofun/data/'+str(pid)+'/')
        pid = str(pid)
        f = open('/home/cofun/data/'+pid+'/data.config', 'wb')
        f.write(dataconfig)
        
    @staticmethod
    def GetConfig(pid):
        try:
            with open('/home/cofun/data/'+str(pid)+'/data.config', 'r') as f:
                return f.read(1000000)
        except:
            return None
        
    @staticmethod
    def GetSpj(pid):
        pid = int(pid)
        try:
            for i in xrange(1, 4):
                if os.path.exists(SPJFILE[i] % pid):
                    return open(SPJFILE[i] % pid,'r').read(1000000)
            return None
        except:
            return None
        
    @staticmethod
    def GetSpjLang(pid, lid):
        pid = int(pid)
        return 'selected' if os.path.exists(SPJFILE[lid] % pid) else None
        
    @staticmethod
    def Config(pid, timlim, memlim):
        Data.Createdir('/home/cofun/data/'+str(pid)+'/')
        autocfg = []
        defaultcfg = []
        cnt = 0
        compre = ''
        strs = []
        find = {'data.config':True}
        timlim = str(timlim)
        memlim = str(memlim)
        start = time.time()
        for root1, dirs1, files1 in os.walk('/home/cofun/data/'+str(pid)+'/', topdown=False):
          root1 = root1.replace('/home/cofun/data/'+str(pid)+'/', '', 1)
          if time.time() - start > 1:
            autocfg.append('error')
            break
          for name1 in files1:
            if find.get(os.path.join(root1, name1), False) or not Data.isdatafile(name1):
              continue
            In = os.path.join(root1, name1)
            find[In] = True
            if time.time() - start > 1:
              break
            for root2, dirs2, files2 in os.walk('/home/cofun/data/'+str(pid)+'/', topdown=False):
              root2 = root2.replace('/home/cofun/data/'+str(pid)+'/', '', 1)
              for name2 in files2:
                if find.get(os.path.join(root2, name2), False) or not Data.isdatafile(name2):
                  continue
                Out = os.path.join(root2, name2)
                if In.replace('in', '').replace('out', '').replace('ou', '').replace('ans', '').replace('txt', '') == \
                  Out.replace('in', '').replace('out', '').replace('ou', '').replace('ans', '').replace('txt', ''):
                  find[Out] = True
                  if In.count('in') < Out.count('in') or In.count('ou') > Out.count('ou') or In.count('ans') > Out.count('ans'):
                    In, Out = Out, In
                  autocfg.append(In + '|' + Out + '|' + timlim + '|' + memlim + '|')
                  cnt += 1
                  strs.append(In)
                  strs.append(Out)
        compre = Data.longestCommonPrefix(strs)
        if cnt:
            autocfg = map(lambda x: x + str(100.0/cnt), autocfg)
        for i in xrange(1, cnt + 1):
            defaultcfg.append(compre + str(i) + '.in|' + compre + str(i) + '.out|' + timlim + '|' + memlim + '|' + str(100.0/cnt))
        autocfg = sorted(autocfg, key = lambda x:(len(x),x))
        defaultcfg = sorted(defaultcfg, key = lambda x:(len(x),x))
        return ('\n'.join(autocfg), '\n'.join(defaultcfg))


