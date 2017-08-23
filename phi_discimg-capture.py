#!/usr/bin/env python
#nj_discimg-capture-fm
#triggered by filemaker, takes 1 argument for barcode that was scanned into FM
#

import glob
import os
import sys
import ConfigParser
import getpass
import subprocess
import time
import imp

def main():
	#initialize via the config file
	dn, fn = os.path.split(os.path.abspath(__file__))
	global conf
	rawconfig = imp.load_source('config',os.path.join(dn,'config.py'))
	conf = rawconfig.config()
	global ut
	ut = imp.load_source("util",os.path.join(dn,"util.py"))
	global log
	log = imp.load_source('log',os.path.join(dn,'logger.py'))
	rawCapturePath = conf.NationalJukebox.VisualArchRawDir
	if not os.path.exists(rawCapturePath):
		os.makedirs(rawCapturePath)
	barcode = sys.argv[1].strip() #grab the lone argument that FM provides
	barcode = barcode.replace("ucsb","cusb") #stupid, stupid bug
	fname = barcode + ".cr2" #make the new filename
	util = imp.load_source('util',os.path.join(dn,"util.py"))
	log.log("started")
	print conf.python
	print os.path.join(dn,"capture-image.py")
	subprocess.call([conf.python,os.path.join(dn,"capture-image.py"),"-nj"])
	time.sleep(3)
	with ut.cd(rawCapturePath): #cd into capture dir
		if os.path.isfile(os.path.join(rawCapturePath,barcode + ".cr2")) or os.path.isfile(os.path.join(rawCapturePath, barcode+ ".CR2")): #error checking, if the file already exists
			log.log(**{"message":"It looks like you already scanned that barcode " + barcode,"level":"warning"})
			print "It looks like you already scanned that barcode"
			a = raw_input("Better check on that")
			sys.exit()
		newest = max(glob.iglob('*.[Cc][Rr]2'), key=os.path.getctime) #sort dir by creation date of .cr2 or .CR2 files
		os.rename(newest,fname) #rename the newest file w/ the barcode just scanned
		log.log("renamed " + newest + " " + fname)
		'''for dirs, subdirs, files in os.walk(os.getcwd()): #error checking, if a file exists with "2016" starting it's name, the raw name off the camera, or if the renaming was otherwise unsuccessful, it'll get flagged here
			for f in files:
				if f.startswith(time.strftime("%Y")):
					#log.log(**{"message":"It looks like you missed scanning a barcode " + barcode,"level":"warning"})
					print "It looks like you missed scanning a barcode"
					a = raw_input("Better check on that")
					sys.exit()'''
		#output = subprocess.check_output([conf.python,os.path.join(conf.scriptRepo,"phi_discimg-out.py"),"-m","single","-so",fname])
		#log.log(output)


main()
log.log("complete")