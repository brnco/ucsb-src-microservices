#!/usr/bin/env python
#avlab-discs
#post-capture-processing for grooved disc materials
import ConfigParser
import getpass
import os
import subprocess
import csv
from distutils import spawn

#check that we have the required software to run this script
def dependencies():
	depends = ['bwfmetaedit','ffmpeg','ffprobe']
	for d in depends:
		if spawn.find_executable(d) is None:
			print "Buddy, you gotta install " + d
			sys.exit()


def main():
	#initialize the stuff
	dn, fn = os.path.split(os.path.abspath(__file__))
	global conf
	rawconfig = imp.load_source('config',os.path.join(dn,'config.py'))
	conf = rawconfig.config()
	global ut
	ut = imp.load_source("util",os.path.join(dn,"util.py"))
	global log
	log = imp.load_source('log',os.path.join(dn,'logger.py'))
	captureDir = conf.discs.rawArchDir
	archRepoDir = conf.discs.archRepoDir
	bextsDir = conf.discs.mtdCaptures
	for dirs, subdirs, files in os.walk(captureDir):
		for f in files:
			if f.endswith(".gpk"):
				with ut.cd(os.pardir(f)):
					os.remove(f)
		for s in subdirs:
			with ut.cd(os.path.join(captureDir,s)):
				endObj1 = s + "b.wav"
				if os.path.isfile(s + "b.wav"):
					subprocess.call(['python',os.path.join(conf.scriptRepo,"makebroadcast.py"),'-ff',endObj1])
					os.remove(endObj1)
					os.rename(s + "c.wav",endObj1)
				if os.path.isfile(s + "a.wav"):
					subprocess.call(['bwfmetaedit','--Originator=US,CUSB,SRC','--OriginatorReference=' + s,'--MD5-Embed-Overwrite', s + "a.wav"])
			subprocess.call(['python',os.path.join(conf.scriptRepo,"hashmove.py"),os.path.join(captureDir,s),os.path.join(archRepoDir,s)])
	return

dependencies()
main()