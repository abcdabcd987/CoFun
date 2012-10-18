import os
import sys
import time
import shutil
import MySQLdb

COMPILE_COMMAND = 'gcc __source.c -o __a.out -Wall'
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
}

def RemoveFiles():
    for root, dirs, files in os.walk('.', topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))

def GetTasks():
    cur.execute('SELECT * FROM Submit WHERE SubmitStatus=0 ORDER BY SubmitID ASC')
    tasks = cur.fetchall()
    return tasks

def Compile():
    os.system(COMPILE_COMMAND + COMPILE_REWRITE)
    info = open('__compile_info.txt', 'r').read()
    return (os.path.exists('__a.out'), info)

def Process(tasks):
    if not tasks:
        return
    for task in tasks:
        print task
        os.chdir('/home/cofun/tmp')
        RemoveFiles()
        fsource = open('__source.c', 'w')
        fsource.write(task['SubmitCode'])
        fsource.close()

        (compile_success, compile_info) = Compile()
        if compile_info:
            print 'HAS INFO'
            cur.execute('UPDATE Submit SET CompilerInfo=%s WHERE SubmitID=%s', (compile_info, task['SubmitID']))
        if not compile_success:
            print 'CE'
            cur.execute('UPDATE Submit SET SubmitStatus=%s, JudgeTime=CURRENT_TIMESTAMP WHERE SubmitID=%s', (RESULT['CE'], task['SubmitID']))
            continue

        basedir = '/home/cofun/data/%d/' % task['ProblemID']
        for line in open(basedir + 'data.config'):
            config = line.strip().split('|')
            if not config:
                continue

            shutil.copyfile(basedir+config[0], '/home/cofun/tmp/input.txt')

        print 'SUCCESS'

def main():
    global con, cur
    try:
        con = MySQLdb.connect('localhost', 'root', '123456', 'cofun')
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
        tasks = GetTasks()
        Process(tasks)
        time.sleep(0.5)
        break

    con.close()

if __name__ == '__main__':
    main()
