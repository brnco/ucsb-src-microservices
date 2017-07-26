#!/usr/bin/env python
#makemp3
#does the best that it can
#takes 1 argument for object to convert to mp3
#keep's input channel config
#outputs 320k mp3
#still gotta add png support for album covers?

import os
import subprocess
import sys
import glob
import re
import argparse
import imp
from distutils import spawn

#check that we have the required software to run this script
def dependencies():
	depends = ['ffmpeg','ffprobe']
	for d in depends:
		if spawn.find_executable(d) is None:
			print "Buddy, you gotta install " + d
			sys.exit()

def id3Check(startObj, assetName): #checks to see if the ID3 tags exist already
	mtdObj = os.path.join(os.path.abspath(os.path.dirname(startObj)),assetName + "-mtd.txt") #name a metadata file
	if not os.path.isfile(mtdObj):
		subprocess.call(['ffmpeg','-i',startObj,'-f','ffmetadata','-y',mtdObj]) #export the id3 metadata that already exists in the media file to this text file
	b = os.path.getsize(mtdObj) #grab the size, in bytes, of the resulting text file
	if b < 39: #40 is the size of a blank ;FFMETADATA1 file
		#encourages users to put this metadata in the broadcast files because that's where it belongs, not just in the access copies
		print " "
		print " "
		print "********************************************************************************"
		print "It appears that there's no associated ID3 tags with this file"
		print "If you'd like to add ID3 tags,"
		print "1) Run makebroadcast.py on the same start file"
		print "2) Run makemp3.py on that broadcast master"
		print " "
		print "By doing it this way, we have ID3 tags for the next time we need them"
		print " "
		print "********************************************************************************"
		os.remove(assetName + "-mtd.txt") #delete it we don't need it here

def makeAudio(startObj, startDir, assetName, EuseChar):	#make the mp3
	endObj = assetName + EuseChar + '.mp3' #give it a name
	with ut.cd(startDir):
		subprocess.call(['ffmpeg','-i',startObj,'-ar','44100','-ab','320k','-f','mp3','-id3v2_version','3','-write_id3v1','1','-y',endObj]) #atually do it

def main():
	#initialize a buncha crap
	dn, fn = os.path.split(os.path.abspath(__file__))
	global conf
	rawconfig = imp.load_source('config',os.path.join(dn,'config.py'))
	conf = rawconfig.config()
	global ut
	ut = imp.load_source("util",os.path.join(dn,"util.py"))
	global log
	log = imp.load_source('log',os.path.join(dn,'logger.py'))
	parser = argparse.ArgumentParser(description="Makes a broadcast-ready file from a single input file")
	parser.add_argument('-so','--startObj',nargs ='?',help='the file to be transcoded',)
	args = parser.parse_args() #create a dictionary instead of leaving args in NAMESPACE land
	startObj = subprocess.check_output(['python',os.path.join(dn,'makestartobject.py'),'-so',args.startObj])
	startObj = startObj.replace("\\",'/')[:-2] #for the windows peeps
	fnamext = os.path.basename(os.path.abspath(startObj)) #filname plus extension of the startObj
	fname, ext = os.path.splitext(fnamext) #split the filename from extension
	SuseChar = fname[-1:] #grabs the last char of file name which is ~sometimes~ the use character
	startDir = os.path.abspath(os.path.join(startObj, os.pardir)) #grabs the directory that this object is in (we'll cd into it later)
	#see what character it is and assign EndUseCharacters accordingly
	if SuseChar == 'a':
		print "archival master"
		assetName = fname[:-1]
		EuseChar = "d"
	elif SuseChar == 'm':
		print "archival master"
		assetName = fname[:-1]
		EuseChar = ""
	elif SuseChar == 'b':
		print "broadcast master"
		assetName = fname[:-1]
		EuseChar = "d"
	elif SuseChar == 'c':
		assetName = fname[:-1]
		EuseChar = "d"
	else:
		assetName = fname
		EuseChar = "d"
	id3Check(startObj, assetName) #call the id3 check function
	makeAudio(startObj, startDir, assetName, EuseChar) #call the makeaudio function

dependencies()
main()