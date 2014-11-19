import os
import sys
import datetime
import time
import shutil
import signal
import MySQLdb
import subprocess
reload(sys)  
sys.setdefaultencoding('utf-8')

COMPILE_COMMAND = {
    1:  'gcc __source.c -o __a.out -Wall',
    2:  'g++ __source.cc -o __a.out -Wall',
    3:  'fpc __source.pas -o__a.out -vewh -Tlinux',
}
COMPILE_REWRITE = ' 1> __compile_info.txt 2>&1'
EXTENSION = {
    1:  'c',
    2:  'cc',
    3:  'pas',
}
RESULT = {
    'CE'    :   1,
    'RUN'   :   2,
    'AC'    :   3,
    'WA'    :   4,
    'RE'    :   5,
    'TLE'   :   6,
    'MLE'   :   7,
    'ND'    :   8,
    'SPJERROR': 9,
}

def demote():
    os.setsid()
    os.setuid(2222)

def RemoveFiles():
    for root, dirs, files in os.walk('.', topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))

def GetTasks():
    cur.execute('SELECT * FROM Submit WHERE SubmitStatus=0 ORDER BY SubmitID ASC')
    tasks = cur.fetchall()
    for task in tasks:
        cur.execute('SELECT SpecialJudge FROM Problem WHERE ProblemID='+str(task['ProblemID']))
        tmp = cur.fetchall()
        task['SpecialJudge'] = tmp[0]['SpecialJudge']
    return tasks

def Compile(lang):
    os.system(COMPILE_COMMAND[lang] + COMPILE_REWRITE)
    info = open('__compile_info.txt', 'r').read()
    return (os.path.exists('__a.out'), info)

def GetDiff(spj, inputfile):
    try:
        if spj:
            p = subprocess.Popen('/home/cofun/data/%d/spj "%s" "%s" "%s" > __diff.txt' % (spj, inputfile, 'answer.txt', 'output.txt'), shell=True, preexec_fn = demote)
            start = time.time()
            flg = True
            exitcode = None
            while time.time() - start <= 1:
                time.sleep(0.1)
                try:
                    exitcode = int(p.poll())
                    flg = False
                    break
                except:
                    pass
            if flg:
                exitcode = p.poll()
            try:
                exitcode = int(exitcode)
            except:
                os.killpg(p.pid,signal.SIGUSR1)
                exitcode = -1
        else:
            exitcode = subprocess.call('/home/cofun/cofun_standard_check "%s" "%s" > __diff.txt' % ('answer.txt', 'output.txt'), shell=True)
        diff = open('__diff.txt', 'r').read()
    except Exception, e:
        print 'Exception', e
        exitcode = -1
        diff = 'Error'
    return (exitcode, diff)

def Process(tasks):
    if not tasks:
        return
    for task in tasks:
        # Update Wait Table Begin
        if task['ContestID']:
            cur.execute('SELECT count(*) FROM Wait WHERE ContestID=%s' % task['ContestID'])
            if (cur.fetchall())[0]['count(*)'] == 0:
                cur.execute('INSERT INTO Wait (ContestID) VALUES (%s)' % task['ContestID'])
                #cur.execute('INSERT INTO Wait (ContestID) VALUES (1010)' % task['ContestID'])
        # Update Wait Table End
        #print task
        os.chdir('/home/cofun/tmp')
        RemoveFiles()
        lang = task['SubmitLanguage']
        spj = task['ProblemID'] if task['SpecialJudge'] else None
        fsource = open('__source.'+EXTENSION[lang], 'w')
        fsource.write(task['SubmitCode'])
        fsource.close()

        (compile_success, compile_info) = Compile(lang)
        if compile_info:
            print '%s  has compile info' % task['SubmitID']
            cur.execute('UPDATE Submit SET CompilerInfo=%s, JudgeTime=CURRENT_TIMESTAMP WHERE SubmitID=%s', (compile_info, task['SubmitID']))
        if not compile_success:
            print '%s  CE' % task['SubmitID']
            cur.execute('UPDATE Submit SET SubmitStatus=%s, JudgeTime=CURRENT_TIMESTAMP WHERE SubmitID=%s', (RESULT['CE'], task['SubmitID']))
            cur.execute('UPDATE Problem SET Submit=Submit+1 WHERE ProblemID=%s', (task['ProblemID']))
            # Update Problem Table Begin
            cur.execute('UPDATE Problem SET Submit=Submit+1 WHERE ProblemID=%s', (task['ProblemID']))
            # Update Problem Table End

            # Update User Table Begin
            if task['ContestID'] == 0:
                cur.execute('UPDATE User SET Submit = Submit+1 WHERE UserID=%s' % task['UserID'])
            # Update User Table End
            print '%s  -----------------------DONE------------------------' % task['SubmitID']
            continue

        basedir = '/home/cofun/data/%d/' % task['ProblemID']
        final = 'AC'
        tottime = 0
        avgmem = 0
        memcnt = 0
        totscored = 0
        flg = True
        try:
            open(basedir + 'data.config')
        except:
            flg = False
        if not flg:
            print '%s  ND' % task['SubmitID']
            cur.execute('UPDATE Submit SET SubmitStatus=%s, JudgeTime=CURRENT_TIMESTAMP, SubmitRunTime=%s, SubmitRunMemory=%s, SubmitScore=%s WHERE SubmitID=%s', (RESULT['ND'], str(tottime), str(0), totscored, task['SubmitID']))
            cur.execute('UPDATE Problem SET Submit=Submit+1 WHERE ProblemID=%s', (task['ProblemID']))
            print 'Data Config Error'
            print '%s  -----------------------DONE------------------------' % task['SubmitID']
            return
        for line in open(basedir + 'data.config'):
            config = line.strip().split('|')
            if len(config) != 5:
                continue
            if not config:
                continue

            cur.execute('UPDATE Submit SET SubmitStatus=%s, JudgeTime=CURRENT_TIMESTAMP WHERE SubmitID=%s', (101+memcnt, task['SubmitID']))

            # config[0]:  input file
            # config[1]:  output file
            # config[2]:  time limit
            # config[3]:  memory limit
            # config[4]:  score
            dataerror = False
            try:
                x = int(config[2])
                x = int(config[3])
                x = float(config[4])
            except:
                dataerror = True
            if dataerror or not os.path.exists(basedir+config[0]) or not os.path.exists(basedir+config[1]):
                print '[%s]%s  on testcase [%s] Dataconfig error' % (time.strftime('%Y-%m-%d %X', time.localtime()), task['SubmitID'], config[0])
                cur.execute('INSERT INTO Result (SubmitID, Result, RunTime, RunMemory, Score, Diff) VALUES (%s, %s, %s, %s, %s, %s)', (task['SubmitID'], RESULT['ND'], 0, 0, 0, ''))
                final = 'ND'
                continue
            shutil.copyfile(basedir+config[0], '/home/cofun/tmp/input.txt')
            os.system('/home/cofun/cofun_client '+config[2]+' '+config[3])

            # RunResult   %d  (0=>NORMAL, 1=>RE, 2=>TLE, 3=>MLE)
            # TimeUsed    %d  (MicroSecond)
            # MemoryUsed  %d  (KBytes)
            # Exitcode    %d  (Exitcode or Signal code)
            result = open('/home/cofun/tmp/__result.txt', 'r').read().strip().split(' ')
            diff = result[3]
            avgmem += int(result[2])
            memcnt += 1
            if int(result[1]) > int(config[2]):
                res = 'TLE'
                final = 'TLE'
            elif int(result[2]) > int(config[3]):
                res = 'MLE'
                final = 'MLE'
            elif result[0] == '1' or result[3] != '0':
                res = 'RE'
                final = 'RE'
            else:
                shutil.copyfile(basedir+config[1], '/home/cofun/tmp/answer.txt')
                (exitcode, diff) = GetDiff(spj, basedir+config[0])
                if spj:
                    print 'spjexitcode:',exitcode
                if exitcode == 0:
                    res = 'AC'
                    tottime += int(result[1])
                elif exitcode <= 5 and exitcode > 0:
                    res = 'WA'
                    final = 'WA'
                    #print diff
                else:
                    res = 'SPJERROR'
                    final = 'SPJERROR'
            score = config[4] if res == 'AC' else '0'
            totscored += float(score)

            print '[%s]%s  on testcase [%s]  %3s  at %4dms  using %7dKBytes memory   with exitcode: %3d' % (time.strftime('%Y-%m-%d %X', time.localtime()), task['SubmitID'], config[0], res, int(result[1]), int(result[2]), int(result[3]))
            cur.execute('INSERT INTO Result (SubmitID, Result, RunTime, RunMemory, Score, Diff) VALUES (%s, %s, %s, %s, %s, %s)', (task['SubmitID'], RESULT[res], result[1], result[2], score, diff))
        if memcnt == 0:
            memcnt = 1
        # Update Problem Table Begin
        cur.execute('UPDATE Problem SET Submit=Submit+1 WHERE ProblemID=%s', (task['ProblemID']))
        cur.execute('SELECT count("*") FROM Submit WHERE UserID=%s AND ProblemID=%s AND SubmitStatus=3' % (task['UserID'], task['ProblemID']))
        if final == 'AC' and (cur.fetchall())[0]['count("*")'] == 0:
            cur.execute('UPDATE Problem SET Solved=Solved+1 WHERE ProblemID=%s', (task['ProblemID']))
        # Update Problem Table End

        # Update User Table Begin
        if task['ContestID'] == 0 and RESULT[final] <= 7:
            cur.execute('UPDATE User SET Submit = Submit+1 WHERE UserID=%s' % task['UserID'])
            if final == 'AC':
                cur.execute('SELECT count(*) FROM Submit WHERE SubmitStatus=3 AND UserID=%s AND ProblemID=%s' % (task['UserID'],task['ProblemID']))
                if (cur.fetchall())[0]['count(*)'] == 0:
                    cur.execute('UPDATE User SET Solved = Solved + 1,Rating = Rating + 3 WHERE UserID=%s' % task['UserID'])
        # Update User Table End

        cur.execute('UPDATE Submit SET SubmitStatus=%s, JudgeTime=CURRENT_TIMESTAMP, SubmitRunTime=%s, SubmitRunMemory=%s, SubmitScore=%s WHERE SubmitID=%s', (RESULT[final], str(tottime), str(avgmem//memcnt), totscored, task['SubmitID']))
        print '%s  -----------------------DONE------------------------' % task['SubmitID']

def GetContestWait():
    cur.execute('SELECT Wait.ContestID, ContestEndTime FROM Contest, Wait WHERE Contest.ContestID=Wait.ContestID')
    wait = cur.fetchall()
    return wait

def RefreshRating(ContestID):
    cur.execute("""            
                SELECT tmp2.UserID, Rating, UserName, SUM(SubmitScore) AS Score, SUM(SubmitRunTime) AS Time FROM
                (
                  SELECT *
                  FROM 
                  (
                    SELECT UserID, ProblemID, SubmitScore, SubmitRunTime FROM Submit WHERE ContestID=%s ORDER BY SubmitID DESC
                  ) as tmp1
                  GROUP BY UserID, ProblemID
                ) as tmp2, User
                WHERE tmp2.UserID=User.UserID GROUP BY UserID ORDER BY Score DESC
                """%ContestID)
    users = cur.fetchall()
    last = -1
    nowrank = 0
    temp = 0
    UpRating = 0.0
    DownRating = 0.0
    cur.execute("select UpRating, DownRating, ContestPrincipal from Contest where ContestID=%s"%ContestID)
    contests = cur.fetchall()
    UpRating = contests[0]["UpRating"]
    DownRating = contests[0]["DownRating"]
    users = filter(lambda x:x["UserID"] != contests[0]["ContestPrincipal"], users)
    UserNum = len(users)
    print 'Processing Contest: ',ContestID
    for user in users:
        temp = temp + 1
        if user["Score"] != last:
            nowrank = temp
            last = user["Score"]
        user["Rank"] = nowrank
        user["e"] = 0.0
        for user2 in users:
            if user2["UserID"] != user["UserID"]:
                user["e"] = user["e"] + 1.0 / (1.0 + 10 ** ((user2["Rating"] - user["Rating"]) / 400.0))
                #print user["Rank"],UpRating
        user["e"] = UserNum - user["e"]
        delta = 0
        if user["Rank"] < user["e"]:
            delta = UpRating * (user["e"] - user["Rank"])
        else:
            delta = DownRating * (user["e"] - user["Rank"])
        user["NowRating"] = user["Rating"] + delta
        
        print user["UserName"], user["Rating"], user["NowRating"]
        cur.execute('UPDATE User SET Rating = %s WHERE UserID=%s'%(user["NowRating"], user["UserID"]))
        cur.execute('SELECT ContestEndTime,ContestTitle FROM Contest where ContestID = %s'%ContestID)
        t = cur.fetchall()
        cur.execute("INSERT INTO RatingChanges (UserID, ContestID, RatingDelta, EndRating, EndTime, Rank, ContestTitle) VALUES (%s, %s, %s, %s, '%s', %s, '%s')"%(user["UserID"], ContestID, delta, user["NowRating"], t[0]["ContestEndTime"], user["Rank"], t[0]["ContestTitle"]))
        #print 'UPDATE User SET Rating = %s WHERE UserID=%s'%(user["NowRating"], user["UserID"])
    print 'Processing Contest Done'

def ProcessContests(wait):
    if not wait:
        return
    for i in wait:
        if datetime.datetime.now() > i['ContestEndTime']:
            cur.execute('SELECT count(*) From Submit WHERE SubmitStatus=0 AND ContestID=%s' % i['ContestID'])
            if (cur.fetchall())[0]['count(*)']:
                continue
            RefreshRating(i["ContestID"])
            cur.execute('UPDATE Submit SET ContestPrincipal=0 WHERE ContestID=%s' % i['ContestID'])
            cur.execute('SELECT SubmitID, SubmitStatus, UserID, ProblemID FROM Submit WHERE ContestID=%s' % i['ContestID'])
            submits = cur.fetchall()
            for task in submits:
                # Update User Table Begin
                if task['SubmitStatus'] <= 7:
                    cur.execute('UPDATE User SET Submit = Submit+1 WHERE UserID=%s' % task['UserID'])
                if task['SubmitStatus'] == 3:
                    cur.execute('SELECT count(*) FROM Submit WHERE SubmitID<%s AND SubmitStatus=3 AND UserID=%s AND ProblemID=%s' % (task['SubmitID'],task['UserID'],task['ProblemID']))
                    if (cur.fetchall())[0]['count(*)'] == 0:
                        cur.execute('UPDATE User SET Solved = Solved + 1,Rating = Rating + 3 WHERE UserID=%s' % task['UserID'])
                # Update User Table End
            cur.execute('DELETE FROM Wait WHERE ContestID=%s' % i['ContestID'])
def main():
    global con, cur
    try:
        con = MySQLdb.connect('localhost', 'root', 'yourpasswd', 'cofun')
        con.set_character_set('utf8')
        cur = con.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SET NAMES utf8;')
        cur.execute('SET CHARACTER SET utf8;')
        cur.execute('SET character_set_connection=utf8;')
    except:
        print "Connect to DB failed!"
        if con:
            con.close()
        return

    while True:
        Contests = GetContestWait()
        ProcessContests(Contests)
        tasks = GetTasks()
        Process(tasks)
        time.sleep(0.5)

    con.close()

if __name__ == '__main__':
    main()
