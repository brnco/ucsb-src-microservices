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
	depends = ['ffmpeg','ffprobe']
	for d in depends:
		if spawn.find_executable(d) is None:
			print "Buddy, you gotta install " + d
			sys.exit()
	return

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
	return

def makeAudio(startObj, startDir, assetName, EuseChar):	#make the mp3
	endObj = assetName + EuseChar + '.mp3' #give it a name
	with cd(startDir):
		subprocess.call(['ffmpeg','-i',startObj,'-ar','44100','-ab','320k','-f','mp3','-id3v2_version','3','-write_id3v1','1','-y',endObj]) #atually do it
	return

def main():
	#initialize a buncha crap
	parser = argparse.ArgumentParser(description="Makes a broadcast-ready file from a single input file")
	parser.add_argument('startObj',nargs ='?',help='the file to be transcoded',)
	args = vars(parser.parse_args()) #create a dictionary instead of leaving args in NAMESPACE land
	startObj = subprocess.check_output(['python','S:/avlab/microservices/makestartobject.py','-so',args["startObj"]])
	startObj = startObj.replace("\\",'/')[:-2] #for the windows peeps
	print startObj
	#if not os.path.exists(startObj): #is it really really real
		#print "Buddy, that's not a file"
		#sys.exit()
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
	return

dependencies()
main()