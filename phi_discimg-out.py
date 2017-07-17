#!/usr/bin/env python
#phi_discimg-out
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
import rawpy
import imageio
from distutils import spawn
	
def idSize(startObjFP):
	with rawpy.imread(startObjFP) as raw:
		height = raw.sizes[0]
		width = raw.sizes[1]
		if int(width) > int(height):
			rotation = '180'
		else:
			rotation = '270'
	if rotation:
		return rotation
	else:
		print "buddy, something's up"
		#log.log({"message":"something is wrong with the rotation calculation","level":"error"})
		sys.exit()
	
def rawpyToTif(startObjFP,fname,rotation,endDir,mmrepo):
	#output = subprocess.check_output(['/usr/local/bin/gm','convert',startObjFP,'-rotate',rotation,'-crop','3648x3648+920','-density','300x300',os.path.join(endDir,fname + ".tif")])
	with rawpy.imread(startObjFP) as raw:
		rgb = raw.postprocess(use_camera_wb=True)
	imageio.imsave(os.path.join(endDir,"rp" + fname + ".tif"),rgb)	
	output = subprocess.check_output(['/usr/local/bin/python',os.path.join(mmrepo,'hashmove.py'),'-nm',os.path.join(endDir,fname + ".tif")])
	log.log(output)

def gmToJpg(startObjFP,fname,endDir,mmrepo):
	#output = subprocess.check_output(['/usr/local/bin/gm','convert',os.path.join(endDir,fname + ".tif"),'-resize','800x800',os.path.join(endDir,fname + ".jpg")])
	with rawpy.imread(startObjFP) as raw:
		rgb = raw.postprocess(use_camera_wb=True)
	imageio.imsave(os.path.join(endDir,fname + ".jpg"),rgb)
	output = subprocess.check_output(['/usr/local/bin/python',os.path.join(mmrepo,'hashmove.py'),'-nm',os.path.join(endDir,fname + ".jpg")])
	log.log(output)

def moveSO(startObjFP,endDir,mmrepo):
	output = subprocess.check_output(['/usr/local/bin/python',os.path.join(mmrepo,'hashmove.py'),startObjFP,endDir])
	log.log(output)
	
def main():
	###INIT VARS###
	parser = argparse.ArgumentParser(description="processes image files for disc labels")
	parser.add_argument('-so','--startObj',dest='so',help="the rawcapture file.cr2 to process, not full path")
	parser.add_argument('-m','--mode',dest='m',choices=["single","batch"],help='mode, process a single file or every file in capture directory')
	args = parser.parse_args()
	#initialize from the config file
	config = ConfigParser.ConfigParser()
	dn, fn = os.path.split(os.path.abspath(__file__)) #grip the path to the directory where ~this~ script is located
	config.read(os.path.join(dn,"microservices-config.ini"))
	#load our utility module
	ut = imp.load_source('util',os.path.join(dn,"util.py"))
	qcDir = ut.drivematch(config.get("NationalJukebox","PreIngestQCDir"))
	#initialize a log file
	global log
	log = imp.load_source('log',os.path.join(dn,'logger.py'))
	
	mmrepo = dn
	imgCaptureDir = ut.drivematch(config.get("NationalJukebox","VisualArchRawDir"))
	log.log("started")
	if args.m == "single":
		startObj = args.so.replace("\\","/")
		if not startObj.startswith(imgCaptureDir):
			for dirs,subdirs,files in os.walk(imgCaptureDir):
				for f in files:
					if f == startObj:
						startObjFP = os.path.join(dirs,startObj)
						break
			if not startObjFP:
				print("Object " + startObj + " does not exist in " + imgCaptureDir)
				foo = raw_input("You should check on that or try a different filename")
				sys.exit()
		else:
			startObjFP = startObj
		fname,ext = os.path.splitext(startObj)
		endDir = os.path.join(qcDir,fname)
		if not os.path.exists(endDir):
			os.makedirs(endDir)
		#get the orientation of the image and set output rotation accordingly
		rotation = idSize(startObjFP)
		
		#convert to tif
		rawpyToTif(startObjFP,fname,rotation,endDir,mmrepo)
		
		#convert to jpg
		#should make jpeg from tiff moving forward
		#rawpyToJpg(startObjFP,fname,endDir,mmrepo)
		
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
				rotation = idSize(startObjFP)
				
				#convert to tif
				rawpyToTif(startObjFP,fname,rotation,endDir,mmrepo)
				
				#convert to jpg
				#should make jpg from tiff moving forward
				#rawpyToJpg(startObjFP,fname,endDir,mmrepo)
				
				#move startObj
				moveSO(startObjFP,endDir,mmrepo)
	
main()
log.log("complete")