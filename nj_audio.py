#nj_audio.py
#processes audio fles for the national jukebox project at UCSB

import glob
import os
import sys
import ConfigParser
import getpass
import time
from distutils import spawn
import subprocess

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
	depends = ['ffmpeg','ffprobe','bwfmetaedit']
	for d in depends:
		if spawn.find_executable(d) is None:
			print "Buddy, you gotta install " + d
			sys.exit()
	return		

	
def main():
	#initialize from the config file
	config = ConfigParser.ConfigParser()
	dn, fn = os.path.split(os.path.abspath(__file__)) #grip the path to the directory where ~this~ script is located
	config.read(os.path.join(dn,"microservices-config.ini"))
	qcDir = config.get('NationalJukebox','PreIngestQCDir')
	batchDir = config.get('NationalJukebox','BatchDir')
	mmrepo = config.get('global','scriptRepo')
	archDir = config.get('NationalJukebox','AudioArchDir')
	broadDir = config.get('NationalJukebox','AudioBroadDir')
	
	#deal with the stupid ucsb bug
	subprocess.call(['python',os.path.join(mmrepo,'rename_ucsbtocusb.py'),archDir])
	subprocess.call(['python',os.path.join(mmrepo,'rename_ucsbtocusb.py'),broadDir])
	
	#make the broadcast files
	with cd(broadDir):
		for dirs, subdirs, files in os.walk(os.getcwd()):
			for f in files:
				if f.endswith(".gpk") or f.endswith(".bak") or f.endswith(".mrk"): #get rid of bs files that wavelab makes
					os.remove(f)
				else:
					subprocess.call(['python',os.path.join(mmrepo,'makebroadcast.py'),f,'-ff','-nj']) #makebroadcast with fades, nj naming
					fname, ext = os.path.splitext(f) #separate just the name of the file
					#pop them into the qc dir in a subdir named after their filename
					#hashmove makes end dir if it doesnt exist already
					subprocess.call(['python',os.path.join(mmrepo,'hashmove.py'),f,os.path.join(qcDir,fname)]) 
	
	#make the archival masters
	with cd(archDir):
		for dirs, subdirs, files in os.walk(os.getcwd()):
			for f in files:
				if f.endswith(".gpk") or f.endswith(".bak") or f.endswith(".mrk"):
					os.remove(f)
				else:
					#first, rename files with an "m" at the end, per nj spec
					fname, ext = os.path.splitext(f)
					mname = fname + "m" + ext
					os.rename(f,mname)
					#embed an md5 hash in the md5 chunk
					print "embedding MD5 info in " + mname
					subprocess.call(['bwfmetaedit','--MD5-Embed',mname])
					#move them to qc dir in subdir named after their canonical filename (actual file name has "m" at end)
					subprocess.call(['python',os.path.join(mmrepo,'hashmove.py'),mname,os.path.join(qcDir,fname)])
	return

dependencies()
main()