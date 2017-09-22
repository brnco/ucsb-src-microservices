#!/usr/bin/env python

import os
import subprocess
import argparse
import re
import time
import shutil
import sys
sys.path.insert(0,"S:/avlab/microservices")
#remove ^ in production
###UCSB modules###
import config as rawconfig
import util as ut
import logger as log
import mtd
import makestartobject as makeso
import makesip
def main():
	global conf
	conf = rawconfig.config()
	alreadythere = []
	problems = []
	'''for dirs, subdirs, files in os.walk(conf.NationalJukebox.PreIngestQCDir):
		for s in subdirs:
			qcfulls = os.path.join(dirs,s)
			scratchfulls = os.path.join(conf.NationalJukebox.scratch,"20170922",s)
			if os.path.exists(scratchfulls):
				shutil.rmtree(qcfulls)'''		
	for dirs, subdirs, files in os.walk(conf.NationalJukebox.PreIngestQCDir):
		for s in subdirs:
			if os.path.exists(os.path.join(conf.NationalJukebox.BatchDir,s)):
				alreadythere.append(s)
				continue
			if len(os.walk(conf.NationalJukebox.BatchDir).next()[1]) < 1000:
				print s
				print os.path.join(dirs,s)
				kwargs = {"materialType":"nj","new_ingest":conf.NationalJukebox.PreIngestQCDir,"repo":conf.NationalJukebox.BatchDir,"scriptRepo":conf.scriptRepo}
				kwargs['filetypes'] = ['m.wav','.wav','.tif','.cr2','.jpg']
				kwargs['assetName'] = s 
				kwargs['fullpath'] = os.path.join(dirs,s)
				packageIsComplete = makesip.verify_package_contents(**kwargs)
				if packageIsComplete:
					moveSuccess = makesip.move_package_toRepo(**kwargs)
					if moveSuccess:
						print "yeah"
					else:
						print "There was a problem moving the SIP to the repo"
						print kwargs['assetName']
						problems.append(kwargs['assetName'])
	print "alreadythere"
	for at in alreadythere:
		print at
	print ""
	print "problems"
	for p in problems:
		print p
if __name__ == '__main__':
	main()