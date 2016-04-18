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

class cd:
    #Context manager for changing the current working directory
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

def dependencies():
	depends = ['ffmpeg','ffprobe','gm']
	for d in depends:
		if spawn.find_executable(d) is None:
			print "Buddy, you gotta install " + d
			sys.exit()
	return

def id3Check(startObj, assetName):
	#call makeid3 if needed
	mtdObj = assetName + "-mtd.txt"
	subprocess.call(['ffmpeg','-i',startObj,'-f','ffmetadata','-y',mtdObj])
	b = os.path.getsize(mtdObj)
	if b < 40:
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
	os.remove(assetName + "-mtd.txt")
	return

def makeAudio(startObj, startDir, assetName, EuseChar):	
	endObj = assetName + EuseChar + '.mp3'
	subprocess.call(['ffmpeg','-i',startObj,'-ar','44100','-ab','320k','-f','mp3','-id3v2_version','3','-write_id3v1','1','-y',endObj])
	return


def main():
	#initialize a buncha crap
	parser = argparse.ArgumentParser(description="Makes a broadcast-ready file from a single input file")
	parser.add_argument('startObj',nargs ='?',help='the file to be transcoded',)
	args = vars(parser.parse_args()) #create a dictionary instead of leaving args in NAMESPACE land
	startObj = args['startObj'].replace("\\",'/') #for the windows peeps
	if not os.path.isfile(startObj):
		print "Buddy, that's not a file"
		sys.exit()
	fnamext = os.path.basename(os.path.abspath(startObj))
	fname, ext = os.path.splitext(fnamext)
	SuseChar = fname[-1:]
	startDir = os.path.abspath(os.path.join(startObj, os.pardir))
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
	id3Check(startObj, assetName)
	makeAudio(startObj, startDir, assetName, EuseChar)
	return

dependencies()
main()