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
	return

	#Context manager for changing the current working directory
class cd:
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

def main():
	#initialize the stuff
	config = ConfigParser.ConfigParser()
	config.read("C:/Users/" + getpass.getuser() + "/microservices-config.ini")
	captureDir = config.get('discs','captureDir')
	archRepoDir = config.get('discs','archRepoDir')
	bextsDir = config.get('discs','mtdCaptures')
	mmrepo = config.get('global','scriptRepo')
	for dirs, subdirs, files in os.walk(captureDir):
		for f in files:
			if f.endswith(".gpk"):
				with cd(os.pardir(f)):
					os.remove(f)
		for s in subdirs:
			with cd(os.path.join(captureDir,s)):
				endObj1 = s + "b.wav"
				if os.path.isfile(s + "b.wav"):
					subprocess.call(['python',os.path.join(mmrepo,"makebroadcast.py"),'-ff',endObj1])
					os.remove(endObj1)
					os.rename(s + "c.wav",endObj1)
				if os.path.isfile(s + "a.wav"):
					subprocess.call(['bwfmetaedit','--Originator=US,CUSB,SRC','--OriginatorReference=' + s,'--MD5-Embed-Overwrite', s + "a.wav"])
			subprocess.call(['python',os.path.join(mmrepo,"hashmove.py"),os.path.join(captureDir,s),os.path.join(archRepoDir,s)])
	return

dependencies()
main()