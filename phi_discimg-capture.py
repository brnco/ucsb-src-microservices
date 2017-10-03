'''
#nj_discimg-capture-fm
#triggered by filemaker, takes 1 argument for barcode that was scanned into FM
'''

import glob
import os
import sys
import argparse
import subprocess
import time
###UCSB modules###
import config as rawconfig
import logger as log
import util as ut
def main():
	'''
	do the thing
	'''
	#initialize via the config file
	global conf
	conf = rawconfig.config()
	parser = argparse.ArgumentParser(description="capture, import, and rename a photo for the PHI project")
	parser.add_argument('barcode', help="the barcode for the disc side you want to capture")
	args = parser.parse_args()
	rawCapturePath = conf.NationalJukebox.VisualArchRawDir
	if not os.path.exists(rawCapturePath):
		os.makedirs(rawCapturePath)
	barcode = args.barcode.strip() #grab the lone argument that FM provides
	barcode = barcode.replace("ucsb", "cusb") #stupid, stupid bug
	fname = barcode + ".cr2" #make the new filename
	log.log("started")
	print conf.python
	print os.path.join(conf.scriptRepo, "capture-image.py")
	subprocess.call([conf.python,os.path.join(conf.scriptRepo,"capture-image.py"), "-nj"])
	time.sleep(3)
	with ut.cd(rawCapturePath): #cd into capture dir
		if os.path.isfile(os.path.join(rawCapturePath, barcode + ".cr2")) or os.path.isfile(os.path.join(rawCapturePath, barcode+ ".CR2")): #error checking, if the file already exists
			log.log(**{"message":"It looks like you already scanned that barcode " + barcode, "level":"warning"})
			print "It looks like you already scanned that barcode"
			a = raw_input("Better check on that")
			sys.exit()
		newest = max(glob.iglob('*.[Cc][Rr]2'), key=os.path.getctime) #sort dir by creation date of .cr2 or .CR2 files
		os.rename(newest, fname) #rename the newest file w/ the barcode just scanned
		log.log("renamed " + newest + " " + fname)

if __name__ == '__main__':
	main()
	log.log("complete")
