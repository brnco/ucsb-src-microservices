#!/usr/bin/env python
#nj_discimg-out
#processes intermediate dng files to tiff
#moves all image files to qcDir

import ConfigParser
import argparse
import subprocess
import os
import sys
import time
import getpass
import re
import imp
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
	
def gmIdentify(startObjFP):
	output = subprocess.check_output(['gm','identify','-verbose',startObjFP])
	#log.log(output)
	match = ''
	match = re.search(r"Geometry:.*\n",output)
	if match:
		geo = match.group()
		geo = geo.replace("Geometry: ","").replace("\n","")
		imgW,imgH = geo.split("x")
		if int(imgW) > int(imgH):
			rotation = '180'
		else:
			rotation = '270'
	if rotation:
		return rotation
	else:
		print "buddy, something's up"
		#log.log({"message":"something is wrong with the rotation calculation","level":"error"})
		sys.exit()
	
def gmToTif(startObjFP,fname,rotation,endDir,mmrepo):
	output = subprocess.check_output(['gm','convert',startObjFP,'-rotate',rotation,'-crop','3648x3648+920','-density','300x300',os.path.join(endDir,fname + ".tif")])
	output = subprocess.check_output(['python',os.path.join(mmrepo,'hashmove.py'),'-nm',os.path.join(endDir,fname + ".tif")])
	#log.log(output)
	
def gmToJpg(startObjFP,fname,endDir,mmrepo):
	output = subprocess.check_output(['gm','convert',os.path.join(endDir,fname + ".tif"),'-resize','800x800',os.path.join(endDir,fname + ".jpg")])
	output = subprocess.check_output(['python',os.path.join(mmrepo,'hashmove.py'),'-nm',os.path.join(endDir,fname + ".jpg")])
	#log.log(output)

def moveSO(startObjFP,endDir,mmrepo):
	output = subprocess.check_output(['python',os.path.join(mmrepo,'hashmove.py'),startObjFP,endDir])
	#log.log(output)
	
def main():
	###INIT VARS###
	parser = argparse.ArgumentParser(description="processes image files for disc labels")
	parser.add_argument('-so','--startObj',dest='so',help="the rawcapture file.cr2 to process, not full path")
	parser.add_argument('-m','--mode',dest='m',choices=["single","batch"],help='mode, process a single file or every file in capture directory')
	args = parser.parse_args()
	#initialize from the config file
	config = ConfigParser.ConfigParser()
	dn, fn = os.path.split(os.path.abspath(__file__)) #grip the path to the directory where ~this~ script is located
	#global log
	#log = imp.load_source('log',os.path.join(dn,'logger.py'))
	config.read(os.path.join(dn,"microservices-config.ini"))
	qcDir = "/Volumes/special/78rpm/avlab/national_jukebox/in_process/pre-ingest-qc"
	#batchDir = config.get('NationalJukebox','BatchDir')
	mmrepo = dn
	imgCaptureDir = "/Volumes/special/78rpm/avlab/national_jukebox/in_process/visual_captures/raw-captures"
	#log.log("started")
	if args.m == "single":
		startObj = args.so.replace("\\","/")
		if not startObj.startswith(imgCaptureDir):
			for dirs,subdirs,files in os.walk(imgCaptureDir):
				for f in files:
					if f == startObj:
						startObjFP = os.path.join(dirs,startObj)
						break
		else:
			startObjFP = startObj
		fname,ext = os.path.splitext(startObj)
		endDir = os.path.join(qcDir,fname)
		if not os.path.exists(endDir):
			os.makedirs(endDir)
		#print startObjFP
		#foo = raw_input("eh")
		#get the orientation of the image and set output rotation accordingly
		rotation = gmIdentify(startObjFP)
		
		#convert to tif
		gmToTif(startObjFP,fname,rotation,endDir,mmrepo)
		
		#convert to jpg
		gmToJpg(startObjFP,fname,endDir,mmrepo)
		
		#move startObj
		moveSO(startObjFP,endDir,mmrepo)

	elif args.m == "batch":
		for dirs,subdirs,files in os.walk(imgCaptureDir):
			for f in files:
				startObj = f
				startObjFP = os.path.join(dirs,f)
				fname,ext = os.path.splitext(f)
				endDir = os.path.join(qcDir,fname)
				if not os.path.exists(endDir):
					os.makedirs(endDir)
				print f
				#get the orientation of the image and set output rotation accordingly
				rotation = gmIdentify(startObjFP)
				
				#convert to tif
				gmToTif(startObjFP,fname,rotation,endDir,mmrepo)
				
				#convert to jpg
				gmToJpg(startObjFP,fname,endDir,mmrepo)
				
				#move startObj
				moveSO(startObjFP,endDir,mmrepo)
	
#log=''
dependencies()
main()
#log.log("complete")