#nj_discimg-out
#processes intermediate dng files to tiff
#moves all image files to qcDir

import ConfigParser
import subprocess
import os
import sys
import time
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

#check that we have the required software to run this script
def dependencies():
	depends = ['gm']
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
	vad = config.get('NationalJukebox','VisualArchRawDir')
	vid = config.get('NationalJukebox','VisualIntermedDir')
	vpd = config.get('NationalJukebox','VisualProcessedDir')
	ren = [vad, vid, vpd] #lets not repeat ourselves here
	blah = os.path.join(vad,time.strftime("%Y-%m-%d"))
	for dirs, subdris, files in os.walk(vid):
		for f in files:
			print f
			#subprocess.call('gm','convert',f,'-crop','3648x3648+920','-density','300x300','-rotate','180'
	for r in ren:
		with cd(r):
			print "blah"
			subprocess.call(['python',os.path.join(mmrepo,'rename_ucsbtocusb.py'),r]) 
	return

dependencies()
main()