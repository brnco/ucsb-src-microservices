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
	#initialize via the config file
	config = ConfigParser.ConfigParser()
	dn, fn = os.path.split(os.path.abspath(__file__)) #grip the path to the directory where ~this~ script is located
	#global log
	#log = imp.load_source('log',os.path.join(dn,'logger.py'))
	config.read(os.path.join(dn,"microservices-config.ini"))
	imgCaptureDir = "/Volumes/special/78rpm/avlab/national_jukebox/in_process/visual_captures/raw-captures" #set a var for the capture directory, mimics structure found in EOS util
	#imgCaptureDir = os.path.join(imgCaptureDir,time.strftime("%Y-%m-%d"))#actual capture directory has today's date in ISO format
	barcode = sys.argv[1] #grab the lone argument that FM provides
	barcode = barcode.replace("ucsb","cusb") #stupid, stupid bug
	fname = barcode + ".cr2" #make the new filename
	#log.log("started")
	subprocess.call(["python",os.path.join(dn,"phi_capture-image.py")])
	with cd(imgCaptureDir): #cd into capture dir
		if os.path.isfile(barcode + ".cr2") or os.path.isfile(barcode + ".CR2"): #error checking, if the file already exists
			log.log(**{"message":"It looks like you already scanned that barcode " + barcode,"level":"warning"})
			print "It looks like you already scanned that barcode"
			a = raw_input("Better check on that")
			sys.exit()
		newest = max(glob.iglob('*.[Cc][Rr]2'), key=os.path.getctime) #sort dir by creation date of .cr2 or .CR2 files
		os.rename(newest,fname) #rename the newest file w/ the barcode just scanned
		#log.log("renamed " + newest + " " + fname)
		'''for dirs, subdirs, files in os.walk(os.getcwd()): #error checking, if a file exists with "2016" starting it's name, the raw name off the camera, or if the renaming was otherwise unsuccessful, it'll get flagged here
			for f in files:
				if f.startswith(time.strftime("%Y")):
					#log.log(**{"message":"It looks like you missed scanning a barcode " + barcode,"level":"warning"})
					print "It looks like you missed scanning a barcode"
					a = raw_input("Better check on that")
					sys.exit()'''
		output = subprocess.check_output(["python",os.path.join(dn,"phi_discimg-out.py"),"-m","single","-so",fname])
		
	return


main()
#log.log("complete")