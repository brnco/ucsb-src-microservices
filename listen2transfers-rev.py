#transfers-qc
#a script that finds the most recent transfers and plays a few seconds from a sample of them

import os
import time
import subprocess
import re
import ConfigParser
import getpass
import argparse
from distutils import spawn

#Context manager for changing the current working directory
class cd:
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

#check that we have the required software to run this script
def dependencies():
	depends = ['ffplay']
	for d in depends:
		if spawn.find_executable(d) is None:
			print "Buddy, you gotta install " + d
			sys.exit()
	return

def doit(sd,start):
	qclist = []
	for dirs, subdirs, files in os.walk(sd):
			for f in files:
				fpath = os.path.join(dirs,f)
				aNum = f.replace("cusb-a","")
				aNum = aNum.replace("a.wav","")
				try:
					if int(aNum) > start: #if the number of seconds that file has existed is less than the number of days we're listneing back
						if fpath.endswith(".wav"): # and if the file is a wav
							qclist.append(fpath) #append it to the lsit of files to search thru
				except:
					pass
	for qcf in qclist: #listen to every file in the list
		foo = raw_input("press any key to listen to " + qcf)
		subprocess.call("ffplay -i " + qcf + " -ss 00:01:00.0") #play the file starting 1minute in
	return
	
def main():
	#initialize a buncha crap
	parser = argparse.ArgumentParser(description="Listen to statistically significant random sampling of recent transfers")
	#parser.add_argument('-t','--tapes',action='store_true',default=False,help='adds 2s heads and tails fades to black/ silence')
	parser.add_argument('-b','--batch',help='the batch, in thousands, to lsiten to, eg: 27000')
	parser.add_argument('-s','--start',type=int,default=0,help='the audioNumber you left off with')
	args = vars(parser.parse_args()) #create a dictionary instead of leaving args in NAMESPACE land
	searchDirs = os.path.join("R:/audio",args['batch'])
	print searchDirs
	blah = raw_input("eh")
	doit(searchDirs,args['start'])
	return

dependencies()	
main()