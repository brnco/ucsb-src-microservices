#!/usr/bin/env python
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
	dn, fn = os.path.split(os.path.abspath(__file__)) #grip the path to the directory where ~this~ script is located
	config.read(os.path.join(dn,"microservices-config.ini"))
	qcDir = config.get('NationalJukebox','PreIngestQCDir')
	batchDir = config.get('NationalJukebox','BatchDir')
	mmrepo = config.get('global','scriptRepo')
	vad = config.get('NationalJukebox','VisualArchRawDir')
	vad = os.path.join(vad,time.strftime("%Y-%m-%d")) #actual capture directory has today's date in ISO format
	vid = config.get('NationalJukebox','VisualIntermedDir')
	vpd = config.get('NationalJukebox','VisualProcessedDir')
	vislist = [vad, vid, vpd] #list of dirs to go thru
	
	if not os.listdir(vad):
		print "Buddy, today's date doesn't match the shooting date for this batch. You should probably rename the capture dir to " + time.strftime("%Y-%m-%d")
		sys.exit()
	
	#first, process the intermediates
	for dirs, subdris, files in os.walk(vid):
		with cd(vid):
			for f in files:
				fname, ext = os.path.splitext(f)
				if not os.path.exists(os.path.join(vpd,fname + ".tif")):
					#convert them to tif and save them to a diff folder
					#in the olden days we had to convert to different dirs
					#keeping that structure just in case :/
					subprocess.call(['gm','convert',f,'-crop','3648x3648+920','-density','300x300','-rotate','180',os.path.join(vpd,fname + ".tif")])
				if not os.path.exists(os.path.join(vpd,fname + ".jpg")):
					#convert them to jpg (for Images_ucsb fm db)
					subprocess.call(['gm','convert',os.path.join(vpd,fname + ".tif"),'-resize','800x800',os.path.join(vpd,fname + ".jpg")])
	
	#move all the files
	for r in vislist:
		subprocess.call(['python',os.path.join(mmrepo,'rename_ucsbtocusb.py'),r]) #deal with the stupid cusb bug	
		for dirs, subdris, files in os.walk(r):
			for f in files:
				fname, ext = os.path.splitext(f)
				subprocess.call(['python',os.path.join(mmrepo,'hashmove.py'),os.path.join(dirs,f),os.path.join(qcDir,fname)])
	return

dependencies()
main()