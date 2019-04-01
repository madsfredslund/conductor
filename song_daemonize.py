#!/usr/bin/python
import os
import sys
import syslog
import signal
import ConfigParser
import getopt
import resource
import threading
import time
#import psycopg2
import atexit
from signal import SIGTERM
from signal import SIGKILL
""" stuff that helps the daemons running and is common
"""
"""! simple use info common for all daemons
""" 
## The default configuration file
cfgfile = '/etc/song/song.cfg'
## The configuration parser
config = ConfigParser.RawConfigParser()
config.read(cfgfile)

def Usage():
    """Prints the usage information."""
    print "-d run as daemon"
    print "-f alternative configuration file (default is: /etc/song/song.cfg)"
    print "-v verbose "
    print "-h help (this help message)"
    
class Daemon:
    """
    A generic daemon class.
         
    Usage: subclass the Daemon class and override the run() method
    """
    def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
	print ""
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile
        
    def daemonize(self):
        """
        do the UNIX double-fork magic, see Stevens' "Advanced
        Programming in the UNIX Environment" for details (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        """
        try: 
            pid = os.fork() 
            if pid > 0:
            # exit first parent
               sys.exit(0) 
        except OSError, e: 
            sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)
         
        # decouple from parent environment
        os.chdir("/") 
        os.setsid() 
        os.umask(0) 
          
        # do second fork
        try: 
           pid = os.fork() 
           if pid > 0:
              # exit from second parent
              sys.exit(0) 
        except OSError, e: 
           sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
           sys.exit(1) 
          
        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = file(self.stdin, 'r')
        so = file(self.stdout, 'a+')
        se = file(self.stderr, 'a+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())
          
        # write pidfile
        atexit.register(self.delpid)
        pid = str(os.getpid())
        file(self.pidfile,'w+').write("%s\n" % pid)

    def delpid(self):
        os.remove(self.pidfile)
   
    def start(self):
        """
        Start the daemon
        """
        # Check for a pidfile to see if the daemon already runs
        try:
           pf = file(self.pidfile,'r')
           print pf.read().strip()
           pid = pf.read().strip()
           pf.close()
        except IOError:
           pid = None
         
           if pid:
              message = "pidfile %s already exist. Daemon already running?\n"
              sys.stderr.write(message % self.pidfile)
              sys.exit(1)
                 
        # Start the daemon
        self.daemonize()
        self.run()
   
    def stop(self):
        """
        Stop the daemon
        """
        # Get the pid from the pidfile
        try:
           pf = file(self.pidfile,'r')
           pid = int(pf.read().strip())
           pf.close()
        except IOError:
           pid = None
         
           if not pid:
              message = "pidfile %s does not exist. Daemon not running?\n"
              sys.stderr.write(message % self.pidfile)
              return # not an error in a restart
   
              # Try killing the daemon process       
        try:
            commandkill = 0
            while commandkill != None:
                os.kill(pid, SIGKILL) # SIGTERM is replaced by SIGKILL to make sure to kill the daemon
                commandkill = os.kill(pid, SIGKILL) # SIGTERM is replaced by SIGKILL to make sure to kill the daemon
                time.sleep(0.1)
                
        except OSError, err:
            err = str(err)
            if err.find("No such process") > 0:
               if os.path.exists(self.pidfile):
                  os.remove(self.pidfile)
               else:
                  print str(err)
                  sys.exit(1)
        
        try:
             os.remove(self.pidfile)
        except Exception, e:
            print e
   
    def restart(self):
        """
        Restart the daemon
        """
        self.stop()
        self.start()
   
    def run(self):
        """
        You should override this method when you subclass Daemon. It will be called after the process has been
        daemonized by start() or restart().
        """
        print 'This is from run' 
   
def writejournal(id, status):
        """Writes information into the journal table.
      
        @param id: The dispatcher id
        @param status: The status of the command
        """
        dbmstr = "dbname=%s  host=%s port=5432 user=%s" % (config.get('dispatcher', 'outputdb'), config.get('dispatcher', 'outputdbhost'), config.get('dispatcher', 'outputdbuser'))
        try:
            conn = psycopg2.connect(dbmstr)
            conn.set_isolation_level(0)
            cursor = conn.cursor()
            cmd = "select * from journal where dispatcher_id = %s" % id
            cursor.execute(cmd)
            res = cursor.fetchall()
            syslog.syslog("Libsong: res: %s" % res)
            if len(res) == 0:
               syslog.syslog("Libsong: Insertinging journal :%s  %s" % (id,status))
           
               cmd = "insert into journal (dispatcher_id,site_id,state) values( %i,%i,'%s' );" % (id, config.getint('node', 'NodeID'), status)
               cursor.execute(cmd)
            else:
               cmd = "update journal set state='%s' where dispatcher_id=%i;" % (status, id)
               syslog.syslog("Libsong: updating journal : %s %s" % (status,id))
               cursor.execute(cmd)
        except:
            print "Libsong: error on journal ID: %s" % str(id)
            syslog.syslog("Libsong: error on journal ID: %s" % str(id))
        finally:
            if cursor is not None:
               cursor.close()
            if conn is not None:
               conn.close()
