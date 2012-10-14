import web
import time
import hashlib
from config import CONFIG

db = web.database(dbn=CONFIG['dbtype'], user=CONFIG['dbuser'], pw=CONFIG['dbpasswd'], db=CONFIG['dbname'])

class Utility(object):
    @staticmethod
    def SHA1(content):
        return hashlib.sha1(content).hexdigest()

class Member(object):
    @staticmethod
    def GetID(nameoremail):
        res = list(db.select("User", what="UserID", where="UserEmail='"+nameoremail+"' or UserName='"+nameoremail+"'"))
        return None if len(res) == 0 else int(res[0]['UserID'])

    @staticmethod
    def GetPassword(userid):
        res = list(db.select("User", what="UserPassword", where="UserID="+str(userid)))
        return None if len(res) == 0 else res[0]['UserPassword']

    @staticmethod
    def Add(username, userpwd, useremail):
        if Member.GetID(username) or Member.GetID(useremail):
            return None
        else:
            return db.insert("User", UserName=username, UserEmail=useremail, UserPassword=Utility.SHA1(userpwd))

class Problem(object):
    @staticmethod
    def Add(title, desc, fin, fout, sin, sout, time, memory, hint, source):
        return db.insert("Problem", ProblemTitle=title, ProblemDescription=desc, ProblemInput=fin, ProblemOutput=fout, ProblemSampleIn=sin, ProblemSampleOut=sout, ProblemTime=time, ProblemMemory=memory, ProblemHint=hint, ProblemSource=source)

    @staticmethod
    def GetList():
        res = list(db.select("Problem", what="ProblemID, ProblemTitle, ProblemSource"))
        return None if len(res) == 0 else res

    @staticmethod
    def Get(problemid):
        res = list(db.select("Problem", what="ProblemID, ProblemTitle, ProblemDescription, ProblemInput, ProblemOutput, ProblemSampleIn, ProblemSampleOut, ProblemTime, ProblemMemory, ProblemHint, ProblemSource", where="ProblemID="+str(problemid)))
        return None if len(res) == 0 else res[0]

    @staticmethod
    def Exist(problemid):
        res = list(db.select("Problem", what="count(*)", where="ProblemID="+str(problemid)))
        return True if res else False

class Status(object):
    @staticmethod
    def Submit(problemid, contestid, userid, lang, code):
        return db.insert("Submit", ProblemID=problemid, ContestID=contestid, UserID=userid, SubmitLanguage=lang, SubmitCode=code, CodeLength=len(code))

    @staticmethod
    def GetList():
        res = list(db.select("Submit, User", what="`SubmitID` ,  `ProblemID` ,  `ContestID` ,  `SubmitTime` ,  `SubmitLanguage` ,  `SubmitCode` ,  `SubmitStatus` ,  `SubmitRunTime` ,  `SubmitRunMemory` , `CodeLength` ,  `JudgeTime` ,  `CompilerInfo` ,  `UserName`", where="`User`.`UserID` =  `Submit`.`UserID`", order="SubmitID DESC"))
        return None if len(res) == 0 else res

    @staticmethod
    def Detail(submitid):
        res1 = list(db.select("Result", what="Result, RunTime, RunMemory", where="SubmitID="+str(submitid), order="ResultID DESC"));
        res2 = list(db.select("Submit", where="SubmitID="+str(submitid)));
        res3 = list(db.select("Result", what="AVG(RunMemory), SUM(RunTime)", where="SubmitID="+str(submitid)))
        return (None, None, None, None) if not res2 else (res1, res2[0], res3[0]['AVG(RunMemory)'], res3[0]['SUM(RunTime)'])

#print Member.Add('test7', 'T7', 'test7@test.com')
#print Member.GetPassword(Member.GetID('test7'))
#print Utility.SHA1('T7')
