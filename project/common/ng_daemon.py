#encoding=UTF8
#code by LP
#2013-8-21

'''
守护进程
'''

import sys 
import os 
 
def NGDaemon(stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'): 
    try: 
        pid = os.fork() 
        if pid > 0: 
            sys.exit(0) 
    except OSError, e: 
        sys.stderr.write("fork #1 failed: (%d) %s\n" % (e.errorno, e.strerror)) 
        sys.exit(1) 
         
    os.chdir('/') 
    os.umask(0) 
    os.setsid() 
     
    try: 
        pid = os.fork() 
        if pid > 0: 
            sys.exit(0) 
    except OSError, e: 
        sys.stderr.write("fork #2 failed: (%d) %s\n" % (e.errorno, e.strerror)) 
        sys.exit(1) 
         
    for f in sys.stdout, sys.stderr: 
        f.flush() 
     
    si = file(stdin, 'r') 
    so = file(stdout, 'a+') 
    se = file(stderr, 'a+', 0) 
    os.dup2(si.fileno(), sys.stdin.fileno()) 
    os.dup2(so.fileno(), sys.stdout.fileno()) 
    os.dup2(se.fileno(), sys.stderr.fileno())