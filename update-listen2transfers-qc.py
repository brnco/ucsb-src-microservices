#!/usr/bin/env python
#transfers-qc
#a script that finds the most recent transfers and plays a few seconds from a sample of them

import os
import time
import subprocess
import re
import ConfigParser
import getpass
import argparse
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
	depends = ['ffplay']
	for d in depends:
		if spawn.find_executable(d) is None:
			print "Buddy, you gotta install " + d
			sys.exit()
	return

def doit(sd,days):
	qclist = []
	youngerThanDays = days * 86400 #multiply it by seconds because that's what getmtime understands
	present = time.time() #now
	for dirs, subdirs, files in os.walk(sd):
			for f in files:
				fpath = os.path.join(dirs,f)
				if (present - os.path.getmtime(fpath)) < youngerThanDays: #if the number of seconds that file has existed is less than the number of days we're listneing back
					if fpath.endswith(".wav"): # and if the file is a wav
						qclist.append(fpath) #append it to the lsit of files to search thru
	foo = raw_input("Press any key to start listening")
	for qcf in qclist[::3]: #listen to every third file in the list
		print qcf
		subprocess.call("ffplay -i " + qcf + " -ss 00:01:00.0") #play the file starting 1minute in
	return
	
def main():
	#initialize a buncha crap
	parser = argparse.ArgumentParser(description="Listen to statistically significant random sampling of recent transfers")
	parser.add_argument('-t','--tapes',action='store_true',default=False,help='adds 2s heads and tails fades to black/ silence')
	parser.add_argument('-c','--cylinders',action='store_true',default=False,help='outputs to stereo (mono is default)')
	parser.add_argument('-nj','--nationaljukebox',action='store_true',default=False,help='extra processing step for National Jukebox files')
	parser.add_argument('-d','--days',default=7,type=int,help='the length of time to lsiten back to, in days')
	args = vars(parser.parse_args()) #create a dictionary instead of leaving args in NAMESPACE land
	searchDirs = [] #these are the dirs we'll search for new items
	audioDirs = [] #"audio" or magnetic tapes have a special thing we gotta do
	if args['tapes'] is True:
		for s in os.listdir("R:/audio/"):
			if s.endswith("0"): #soooo many dirs in this parent dir but everything we want to search will end with a 0
				audioDirs.append(os.path.join("R:/audio",s)) #make a list of dirs, 0000 - 27000
		audioDirs.reverse() #search thru later dirs first because they're more likely to have new stuff
		for ad in audioDirs: 
			searchDirs.append(ad) #pop each dir 1 at a time into our searchDirs list
	if args['cylinders'] is True:
		searchDirs.append("R:/Cylinders/avlab/audio_captures/") #search the capture directory (things that havent been processed)
		searchDirs.append("R:/Cylinders") #search the repo (things that have been processed)
	if args['nationaljukebox'] is True:
		searchDirs.append("R:\78rpm\avlab\national_jukebox\in_process\pre-ingest-QC") #these files have been processed and they're waiting for images (generally)
	
	#print searchdirs
	#foo = raw_input("eh")
	for sd in searchDirs:
		doit(sd,args['days'])
	return

dependencies()	
main()