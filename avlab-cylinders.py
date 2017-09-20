#!/usr/bin/env python
#avlab-cylinders
#processes cylinders
#takes broadcast master, adds ID3 tags and 2s heads and tails fades (via makebroadcast.py)
#makes an mp3
#makes a SIP and movs to R:/Cylinders share (via hashmove.py)

import os
import subprocess
import sys
import glob
import re
import getpass
import argparse
###UCSB modules###
import config as rawconfig
import util as ut
import logger as log
import mtd
import makestartobject as makeso
	

def main():
	###INIT VARS###
	global conf
	conf = rawconfig.config()
	log.log("started")
	captureDir = conf.cylinders.new_ingest
	repoDir = conf.cylinders.repo
	logDir = conf.cylinders.avlab
	parser = argparse.ArgumentParser(description="batch processes cylinder transfers")
	parser.add_argument('-m',dest='m',choices=['batch','single'],default=False,help='single mode, for processing a single transfer')
	parser.add_argument('-i','--input',dest='i',help="the rawcapture file.wav to process, single mode only")
	args = parser.parse_args()
	###END INIT###
	if args.m is 'batch':
		for dirs, subdirs, files in os.walk(captureDir):
			for s in subdirs:#for each folder in our capture directory
				with ut.cd(os.path.join(captureDir, s)):
					print "Processing Cylinder" + s
					###DELETE BS###
					for f in os.listdir(os.getcwd()):
						if f.endswith(".gpk") or f.endswith(".bak") or f.endswith(".mrk"): #if the files in each capture dir end with some bs
							os.remove(f) #delete it
					###END BS###
					###VALIDATE###
					startObj = 'cusb-cyl' + s + 'b.wav'
					interObj = 'cusb-cyl' + s + 'c.wav'
					if not os.path.exists(startObj): #if we don't have a b.wav file in the dir we should just stop
						if os.path.exists('cusb-cy' + s + 'b.wav'): #check to see that it wasnt just misnamed at capture
							os.rename(os.path.join(captureDir,s,'cusb-cy'+s+'b.wav'),os.path.join(captureDir,s,'cusb-cyl'+s+'b.wav'))
						if os.path.exists('cusb-cy' + s + 'a.wav'): #check to see that it wasnt just misnamed at capture
							os.rename(os.path.join(captureDir,s,'cusb-cy'+s+'a.wav'),os.path.join(captureDir,s,'cusb-cyl'+s+'a.wav'))
						else:	
							continue
					###END VALIDATE###
					###DO FFMPEG###
					#calls makebroadcast.py and tells it to insert 2s fades and normalize to -1.5db
					subprocess.call(['python',os.path.join(conf.scriptRepo,'makebroadcast.py'),'-so',startObj,'-ff','-n','-c'])
					subprocess.call(['python',os.path.join(conf.scriptRepo,'makemp3.py'),'-so',startObj]) #calls makemp3.py on the new broadcast master
					###END FFMPEG###
				###LOG IT###
				#opens a log and write "Cylinder12345" for each cylinder processed so we can change their catalog records later
				with open(os.path.join(logDir,'to-update.txt'),'a') as t:
					t.write("Cylinder" + s + "\n")
				###END LOG###
				###MOVE IT###
				#based on how we have our repo set up, find which set of 1000 files this cylinder belongs in
				endDirThousand = str(s)
				if len(endDirThousand) < 5:
					endDirThousand = endDirThousand[:1] + "000"
				else:
					endDirThousand = endDirThousand[:2] + "000"
				endDir = os.path.abspath(os.path.join(repoDir,endDirThousand,s)) #set a destination
				subprocess.call(['python',os.path.join(conf.scriptRepo,'hashmove.py'),os.path.join(dirs,s),endDir]) #hashmove the file to its destination
				###END MOVE###

if __name__ == "__main__":
	main()
