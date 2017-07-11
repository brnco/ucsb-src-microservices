import logging
import inspect
import os
import psutil
import time
import imp
import getpass
import unittest

class testAdditionalMethods(unittest.TestCase):
	def test_current_pid(self):
		self.assertEqual(makePID(os.getpid()),os.getpid())

#makes a processID if none provided
#searches up the stack for the top-most parent pid
def makePID(pid):
	while True:
		_pid = pid #set _pid to "old" pid
		try:
			pid = psutil.Process(pid).ppid() #try to set a new pid to the parent of the old pid
			if psutil.Process(pid).name() == "cmd.exe" or psutil.Process(pid).name() == 'bash': #if the parent of the old pid is cmd.exe
				return _pid #return the old pid
		except:	#if the assignment didn't work
			return _pid #return the old pid

#actually does the thing	
def write(message,pid,level,caller,fname):
	logging.basicConfig(filename=fname,format='%(asctime)s %(levelname)s %(name)s %(process)d-%(threadName)s:\n %(message)s',datefmt='%Y-%m-%d %I:%M:%S %p',level=logging.DEBUG)
	logging.getLogger(caller).info(str(message))

#parses input, formats for write	
def log(message,**kwargs):
	###INIT FROM CONFIG FILE###
	dn, fn = os.path.split(os.path.abspath(__file__)) #grip the path to the directory where ~this~ script is located
	global conf
	rawconfig = imp.load_source('config',os.path.join(dn,'config.py'))
	conf = rawconfig.config()
	logLoc = conf.log.location
	global ut
	ut = imp.load_source("util",os.path.join(dn,"util.py"))
	###END INIT###
	###MAKE COMPONENTS###
	if not 'pid' in kwargs:
		pid = str(makePID(os.getpid()))
	else:
		pid = str(kwargs['pid'])
	if not 'caller' in kwargs:
		frame = inspect.stack()[1]
		caller = os.path.basename(frame[1])
	else:
		caller = kwargs['caller']
	if not 'level' in kwargs:
		level = "info"
	else:
		level = kwargs['level']
	pidTime = str(psutil.Process(int(pid)).create_time())	
	fname = os.path.join(logLoc,time.strftime("%Y-%m-%d"),getpass.getuser()+ "-" + pid + "-" + pidTime + ".log") #logs saved per day (prevent PID-named files from containing too many runs)
	if not os.path.exists(os.path.dirname(fname)):
		os.makedirs(os.path.dirname(fname))
	###END MAKE###
	###DO THE THING###
	write(message,pid,level,caller,fname)
	###DONE###
	
if __name__ == '__main__':
    unittest.main()	