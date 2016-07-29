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
	config.read("C:/Users/" + getpass.getuser() + "/microservices-config.ini")
	qcDir = config.get('NationalJukebox','PreIngestQCDir')
	batchDir = config.get('NationalJukebox','BatchDir')
	mmrepo = config.get('global','scriptRepo')
	archDir = config.get('NationalJukebox','AudioArchDir')
	broadDir = config.get('NationalJukebox','AudioBroadDir')
	subprocess.call(['python',os.path.join(mmrepo,'rename_ucsbtocusb.py'),archDir])
	subprocess.call(['python',os.path.join(mmrepo,'rename_ucsbtocusb.py'),broadDir])
	with cd(broadDir):
		for dirs, subdirs, files in os.walk(os.getcwd()):
			for f in files:
				if f.endswith(".gpk") or f.endswith(".bak") or f.endswith(".mrk"):
					os.remove(f)
				else:
					#subprocess.call(['python',os.path.join(mmrepo,'makebroadcast.py'),f,'-ff','-nj'])
					fname, ext = os.path.splitext(f)
					subprocess.call(['python',os.path.join(mmrepo,'hashmove.py'),f,os.path.join(qcDir,fname)])
	with cd(archDir):
		for dirs, subdirs, files in os.walk(os.getcwd()):
			for f in files:
				if f.endswith(".gpk") or f.endswith(".bak") or f.endswith(".mrk"):
					os.remove(f)
				else:
					fname, ext = os.path.splitext(f)
					mname = fname + "m" + ext
					os.rename(f,mname)
					print "embedding MD5 info in " + mname
					subprocess.call(['bwfmetaedit','--MD5-Embed',mname])
					subprocess.call(['python',os.path.join(mmrepo,'hashmove.py'),mname,os.path.join(qcDir,fname)])
	return

dependencies()
main()