#nj_discimg-capture-fm
#triggered by filemaker, takes 1 argument for barcode that was scanned into FM
#

import glob
import os
import sys
import ConfigParser
import getpass
import time

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
	config.read(os.path.join(dn,"microservices-config.ini"))
	vad = config.get('NationalJukebox','VisualArchRawDir') #set a var for the capture directory, mimics structure found in EOS util
	vad = os.path.join(vad,time.strftime("%Y-%m-%d"))
	print vad#actual capture directory has today's date in ISO format
	barcode = sys.argv[1] #grab the lone argument that FM provides
	barcode = barcode.replace("ucsb","cusb") #stupid, stupid bug
	fname = barcode + ".cr2" #make the new filename
	with cd(vad): #cd into capture dir
		if os.path.isfile(barcode + ".cr2") or os.path.isfile(barcode + ".CR2"): #error checking, if the file already exists
			print "Buddy, looks like you already scanned that barcode"
			a = raw_input("Better check on that")
			sys.exit()
		newest = max(glob.iglob('*.[Cc][Rr]2'), key=os.path.getctime) #sort dir by creation date of .cr2 or .CR2 files
		os.rename(newest,fname) #rename the newest file by the barcode just scanned
		for dirs, subdirs, files in os.walk(os.getcwd()): #error checking, if a file exists with "2016" starting it's name, the raw name off the camera, or if the renaming was otherwise unsuccessful, it'll get flagged here
			for f in files:
				if f.startswith(time.strftime("%Y")):
					print "Buddy, looks like you missed scanning a barcode"
					a = raw_input("Better check on that")
					sys.exit()
	return

main()
