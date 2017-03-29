#!/usr/bin/env python
#avlab-cylinders
#processes cylinders
#takes broadcast master, adds ID3 tags and 2s heads and tails fades (via makebroadcast.py)
#makes an mp3
#makes a SIP and movs to R:/Cylinders share (via hashmove.py)

import os
import subprocess
import sys
import glob
import re
import ConfigParser
import getpass
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

#find if we have the required software to complete this script
def dependencies():
	depends = ['ffmpeg','ffprobe']
	for d in depends:
		if spawn.find_executable(d) is None:
			print "Buddy, you gotta install " + d
			sys.exit()
	return
	
def main():
	###INIT VARS###
	config = ConfigParser.ConfigParser()
	dn, fn = os.path.split(os.path.abspath(__file__)) #grip the path to the directory where ~this~ script is located
	config.read(os.path.join(dn,"microservices-config.ini"))
	captureDir = config.get('cylinders','new_ingest')
	repoDir = config.get('cylinders','repo')
	logDir = config.get('cylinders','avlab')
	mmrepo = config.get('global','scriptRepo')
	###END INIT###
	
	for dirs, subdirs, files in os.walk(captureDir):
		for s in subdirs:#for each folder in our capture directory
			with cd(os.path.join(captureDir, s)):
				print "Processing Cylinder" + s
				###DELETE BS###
				for f in os.listdir(os.getcwd()):
					if f.endswith(".gpk") or f.endswith(".bak") or f.endswith(".mrk"): #if the files in each capture dir end with some bs
						os.remove(f) #delete it
				###END BS###
				###VALIDATE###
				startObj = 'cusb-cyl' + s + 'b.wav'
				interObj = 'cusb-cyl' + s + 'c.wav'
				if not os.path.exists(startObj): #if we don't have a b.wav file in the dir we should just stop
					print "Buddy, somethings not right here"
					sys.exit()
				###END VALIDATE###
				###DO FFMPEG###
				else:
					#calls makebroadcast.py and tells it to insert 2s fades and normalize to -1.5db, MAKEBROADCAST CALLS MAKEMP3
					subprocess.call(['python',os.path.join(mmrepo,'makebroadcast.py'),'-so',startObj,'-ff','-n','-c','-mp3'])
					#subprocess.call(['python',os.path.join(mmrepo,'makemp3.py'),startObj]) #calls makemp3.py on the new broadcast master
				###END FFMPEG###
			###LOG IT###
			#opens a log and write "Cylinder12345" for each cylinder processed so we can change their catalog records later
			with open(os.path.join(logDir,'to-update.txt'),'a') as t:
				t.write("Cylinder" + s + "\n")
			###END LOG###
			###MOVE IT###
			#based on how we have our repo set up, find which set of 1000 files this cylinder belongs in
			endDirThousand = str(s)
			if len(endDirThousand) < 5:
				endDirThousand = endDirThousand[:1] + "000"
			else:
				endDirThousand = endDirThousand[:2] + "000"
			endDir = os.path.abspath(os.path.join(repoDir,endDirThousand,s)) #set a destination
			subprocess.call(['python','hashmove.py',os.path.join(dirs,s),endDir]) #hashmove the file to its destination
			###END MOVE###

dependencies()
main()
