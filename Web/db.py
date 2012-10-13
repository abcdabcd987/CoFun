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

#print Member.Add('test7', 'T7', 'test7@test.com')
#print Member.GetPassword(Member.GetID('test7'))
#print Utility.SHA1('T7')
