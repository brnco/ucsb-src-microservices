#transfers-qc
#a script that finds the most recent transfers and plays a few seconds from a sample of them

import os
import time
import subprocess
import re
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

def doit(sd):
	qclist = []
	olderThanDays = 7 * 86400
	present = time.time()
	for dirs, subdirs, files in os.walk(sd):
			for f in files:
				fpath = os.path.join(dirs,f)
				if (present - os.path.getmtime(fpath)) < olderThanDays:
					if fpath.endswith(".wav"):
						qclist.append(fpath)
	for qcf in qclist[::3]:
		print qcf
		subprocess.call("ffplay -i " + qcf + " -ss 00:01:00.0 -t 15 -autoexit")
	return
	
def main():
	audioDirs = []
	for s in os.listdir("R:/audio/"):
		if s.endswith("0"):
			audioDirs.append(os.path.join("R:/audio",s))
	audioDirs.reverse()
	print audioDirs
	#foo = raw_input("eh")
	searchDirs = ["R:\78rpm\avlab\national_jukebox\in_process\pre-ingest-QC","R:/Cylinders/avlab/audio_captures/"]
	#for sd in searchDirs:
		#doit(sd)
	for sd in audioDirs:
		doit(sd)
	return

dependencies()	
main()