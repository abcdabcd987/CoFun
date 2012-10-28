import web
import time
import hashlib
import datetime
import markdown2
from config import CONFIG

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
    def GetID(nameoremail):
        res = list(db.select("User", what="UserID", where="UserEmail='"+nameoremail+"' or UserName='"+nameoremail+"'"))
        return None if len(res) == 0 else int(res[0]['UserID'])

    #@staticmethod
    #def GetPassword(userid):
    #    res = list(db.select("User", what="UserPassword", where="UserID="+str(userid)))
    #    return None if len(res) == 0 else res[0]['UserPassword']

    @staticmethod
    def GetInfo(userid):
        res = list(db.select("User", where="UserID="+str(userid)))
        return None if len(res) == 0 else res[0]

    @staticmethod
    def Add(username, userpwd, useremail):
        if Member.GetID(username) or Member.GetID(useremail):
            return None
        else:
            return db.insert("User", UserName=username, UserEmail=useremail, UserPassword=Utility.SHA1(userpwd))

    @staticmethod
    def GetLastLanguage(userid):
        res = list(db.select("Submit", what="SubmitLanguage", limit=1, where="UserID="+str(userid), order="SubmitID DESC"))
        return res[0]['SubmitLanguage'] if res else None

class Problem(object):
    @staticmethod
    def Add(title, desc, fin, fout, sin, sout, time, memory, hint, source):
        return db.insert("Problem", ProblemTitle=title, ProblemDescription=desc, ProblemInput=fin, ProblemOutput=fout, ProblemSampleIn=sin, ProblemSampleOut=sout, ProblemTime=time, ProblemMemory=memory, ProblemHint=hint, ProblemSource=source)

    @staticmethod
    def GetList(offset, limit):
        res = list(db.select("Problem", what="ProblemID, ProblemTitle, ProblemSource", offset=offset, limit=limit))
        return None if len(res) == 0 else res

    @staticmethod
    def Get(problemid):
        res = db.select("Problem", what="ProblemID, ProblemTitle, ProblemDescription, ProblemInput, ProblemOutput, ProblemSampleIn, ProblemSampleOut, ProblemTime, ProblemMemory, ProblemHint, ProblemSource", where="ProblemID="+str(problemid))
        if not res:
            return None
        res = list(res)[0]
        res.ProblemDescription = markdown2.markdown(res.ProblemDescription)
        res.ProblemInput = markdown2.markdown(res.ProblemInput)
        res.ProblemOutput = markdown2.markdown(res.ProblemOutput)
        return res

    @staticmethod
    def Count():
        return int(list(db.select("Problem", what="count(*)"))[0]["count(*)"])

    @staticmethod
    def Exist(problemid):
        res = list(db.select("Problem", what="count(*)", where="ProblemID="+str(problemid)))
        return True if res else False

class Status(object):
    @staticmethod
    def Submit(problemid, contestid, userid, lang, code):
        return db.insert("Submit", ProblemID=problemid, ContestID=contestid, UserID=userid, SubmitLanguage=lang, SubmitCode=code, CodeLength=len(code))

    @staticmethod
    def Count():
        return int(list(db.select("Submit", what="count(*)"))[0]["count(*)"])

    @staticmethod
    def GetList(offset, limit):
        res = list(db.select("Submit, User", what="SubmitID, Submit.UserID, User.UserName, ProblemID, ContestID, SubmitStatus, SubmitScore, SubmitRunMemory, SubmitRunTime, SubmitLanguage, CodeLength, SubmitTime", where="`User`.`UserID` =  `Submit`.`UserID`", order="SubmitID DESC", offset=offset, limit=limit))
        if res:
            for submit in res:
                submit.SubmitScore = "%3.1f" % float(submit.SubmitScore)
        return None if len(res) == 0 else res

    @staticmethod
    def Detail(submitid):
        res1 = list(db.select("Result", what="Result, RunTime, RunMemory, Score, Diff", where="SubmitID="+str(submitid)));
        res2 = list(db.select("Submit", where="SubmitID="+str(submitid)));
        res3 = list(db.select("Result", what="AVG(RunMemory), SUM(RunTime)", where="SubmitID="+str(submitid)))
        if res2:
            res2 = res2[0]
            res2.SubmitScore = '%3.1f' % res2.SubmitScore
            for testcase in res1:
                testcase.Score = '%3.1f' % testcase.Score
        return (None, None, None, None) if not res2 else (res1, res2, res3[0]['AVG(RunMemory)'], res3[0]['SUM(RunTime)'])

class Contest(object):
    @staticmethod
    def Add(title, stime, etime, desc, prin, probs):
        cid = db.insert("Contest", ContestTitle=title, ContestStartTime=stime, ContestEndTime=etime, ContestDescription=desc, ContestPrincipal=prin)
        for prob in probs:
            try:
                p = int(prob)
            except:
                p = 0
            if p >= 1000:
                db.insert("ContestProblem", ContestID=cid, ProblemID=p)
        return cid

    @staticmethod
    def Get(cid):
        contest = db.select("Contest", where="ContestID="+str(cid))
        prob = db.select("ContestProblem, Problem", what="Problem.ProblemID, Problem.ProblemTitle", where="ContestProblem.ContestID="+str(cid)+" AND Problem.ProblemID=ContestProblem.ProblemID")
        if not contest:
            return (None, None)
        else:
            contest = list(contest)[0]
            contest.ContestDescription = markdown2.markdown(contest.ContestDescription)
            contest.FullScore = list(db.select("ContestProblem", what="COUNT(*) AS Count", where="ContestID="+str(cid)))[0]['Count']*100.0
            return (contest, list(prob)) if prob else (contest, None)

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
            return (contest, prob)

    @staticmethod
    def GetList(offset, limit):
        res = list(db.select("Contest", offset=offset, limit=limit, order="ContestID DESC"))
        return None if len(res) == 0 else res

    @staticmethod
    def Count():
        return int(list(db.select("Contest", what="count(*)"))[0]["count(*)"])

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
    def IsProblemNotDone(pid, cid=0):
        contests = db.select("ContestProblem", where="ProblemID="+str(pid))
        if not contests:
            return False
        for contest in contests:
            if contest.ContestID == cid:
                return False
            if Contest.GetStatusByID(contest.ContestID) != 3:
                return True
        return False

    @staticmethod
    def GetRank(cid):
        res = db.select('(SELECT * FROM (SELECT UserID, ProblemID, SubmitScore FROM Submit WHERE ContestID='+str(cid)+' ORDER BY SubmitID DESC) as tmp1 GROUP BY UserID, ProblemID) as tmp2, User', what='tmp2.UserID, UserName, SUM(SubmitScore) AS Score', where='tmp2.UserID=User.UserID', group='UserID', order='Score DESC')
        return list(res) if res else None
        #SELECT tmp2.UserID, UserName, SUM(SubmitScore) AS Score FROM
        #(
        #  SELECT *
        #  FROM 
        #  (
        #    SELECT UserID, ProblemID, SubmitScore FROM Submit WHERE ContestID=1000 ORDER BY SubmitID DESC
        #  ) as tmp1
        #  GROUP BY UserID, ProblemID
        #) as tmp2, User
        #WHERE tmp2.UserID=User.UserID GROUP BY UserID ORDER BY Score DESC

class Series(object):
    @staticmethod
    def Add(title, desc, probs):
        cid = db.insert("Series", SeriesTitle=title, SeriesDescription=desc)
        for prob in probs:
            try:
                p = int(prob)
            except:
                p = 0
            if p >= 1000:
                db.insert("SeriesProblem", SeriesID=cid, ProblemID=p)
        return cid

    @staticmethod
    def Get(cid):
        series = db.select("Series", where="SeriesID="+str(cid))
        prob = db.select("SeriesProblem, Problem", what="Problem.ProblemID, Problem.ProblemTitle", where="SeriesProblem.SeriesID="+str(cid)+" AND Problem.ProblemID=SeriesProblem.ProblemID")
        if not series:
            return (None, None)
        else:
            series = list(series)[0]
            series.SeriesDescription = markdown2.markdown(series.SeriesDescription)
            series.FullScore = list(db.select("SeriesProblem", what="COUNT(*) AS Count", where="SeriesID="+str(cid)))[0]['Count']*100.0
            return (series, list(prob)) if prob else (series, None)

    @staticmethod
    def GetList(offset, limit):
        res = list(db.select("Series", offset=offset, limit=limit, order="SeriesID DESC"))
        return None if len(res) == 0 else res

    @staticmethod
    def Count():
        return int(list(db.select("Series", what="count(*)"))[0]["count(*)"])

    @staticmethod
    def GetRank(sid):
        res = db.select('( SELECT ProblemId, SubmitScore, UserID FROM ( SELECT ProblemID, UserID, SubmitScore FROM Submit WHERE ProblemID IN ( SELECT ProblemID FROM SeriesProblem WHERE SeriesID='+str(sid)+') ORDER BY SubmitID DESC) AS tmp1 GROUP BY ProblemID, UserID) AS tmp2, User', what="tmp2.UserID, UserName, SUM(SubmitScore) AS Score", group='UserID', order='Score DESC', where="User.UserID=tmp2.UserID")
        return list(res) if res else None
        #SELECT tmp2.UserID, UserName, SUM(SubmitScore) AS Score FROM
        #(
        #  SELECT ProblemId, SubmitScore, UserID FROM
        #  (
        #    SELECT ProblemID, UserID, SubmitScore FROM Submit WHERE ProblemID IN 
        #    (
        #      SELECT ProblemID FROM SeriesProblem WHERE SeriesID=sid
        #    ) ORDER BY SubmitID DESC
        #  ) AS tmp1 GROUP BY ProblemID, UserID
        #) AS tmp2, User WHERE User.UserID=tmp2.UserID GROUP BY UserID ORDER BY Score DESC ;

