import web
import time
import hashlib
import datetime
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
        res = list(db.select("Problem", what="ProblemID, ProblemTitle, ProblemDescription, ProblemInput, ProblemOutput, ProblemSampleIn, ProblemSampleOut, ProblemTime, ProblemMemory, ProblemHint, ProblemSource", where="ProblemID="+str(problemid)))
        return None if len(res) == 0 else res[0]

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
        res = list(db.select("Submit, User", what="`SubmitID` ,  `ProblemID` ,  `ContestID` ,  `SubmitTime` ,  `SubmitLanguage` ,  `SubmitCode` ,  `SubmitStatus` ,  `SubmitRunTime` ,  `SubmitRunMemory` , `CodeLength` ,  `JudgeTime` ,  `CompilerInfo` ,  `UserName`", where="`User`.`UserID` =  `Submit`.`UserID`", order="SubmitID DESC", offset=offset, limit=limit))
        return None if len(res) == 0 else res

    @staticmethod
    def Detail(submitid):
        res1 = list(db.select("Result", what="Result, RunTime, RunMemory", where="SubmitID="+str(submitid)));
        res2 = list(db.select("Submit", where="SubmitID="+str(submitid)));
        res3 = list(db.select("Result", what="AVG(RunMemory), SUM(RunTime)", where="SubmitID="+str(submitid)))
        return (None, None, None, None) if not res2 else (res1, res2[0], res3[0]['AVG(RunMemory)'], res3[0]['SUM(RunTime)'])

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
            return (list(contest)[0], list(prob)) if prob else (list(contest)[0], None)

    @staticmethod
    def GetProblem(cid, pid):
        contest = db.select("Contest", where="ContestID="+str(cid))
        prob = db.select("ContestProblem, Problem", what="Problem.*", where="ContestProblem.ContestID="+str(cid)+" AND Problem.ProblemID=ContestProblem.ProblemID AND Problem.ProblemID="+str(pid))
        if not contest or not prob:
            return (None, None)
        else:
            return (list(contest)[0], list(prob)[0])

    @staticmethod
    def GetList(offset, limit):
        res = list(db.select("Contest", offset=offset, limit=limit, order="ContestID DESC"))
        return None if len(res) == 0 else res

    @staticmethod
    def Count():
        return int(list(db.select("Problem", what="count(*)"))[0]["count(*)"])

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

#print Member.Add('test7', 'T7', 'test7@test.com')
#print Member.GetPassword(Member.GetID('test7'))
#print Utility.SHA1('T7')
