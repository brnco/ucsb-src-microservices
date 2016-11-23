#!/usr/bin/env python

import os
import subprocess
import sys
import glob
import re
import argparse
import ConfigParser
import getpass
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

#check that we have required software installed
def dependencies():
	depends = ['ffmpeg','ffprobe']
	for d in depends:
		if spawn.find_executable(d) is None:
			print "Buddy, you gotta install " + d
			sys.exit()
	return

def makeIt(startObj, archRepoDir):	
	'''with open(os.path.join(archRepoDir,startObj,startObj + "yt.txt"),"r") as f:
		overlay = f.read()
	overlay = str(overlay)'''
	txtfile = os.path.join(archRepoDir,startObj,startObj + "yt.txt")
	txtfile = txtfile.replace("\\","/")
	txtfile = txtfile.replace(":","\\\:")
	print txtfile
	foo = raw_input("eh")
	with cd(os.path.join(archRepoDir,startObj)):
		subprocess.call(['ffmpeg','-f','lavfi','-i','color=c=black:s=1920x1080:d=10','-vcodec','libx264','-preset','slow','-crf','20',"headblack.mp4"])
		subprocess.call(['ffmpeg','-i',"headblack.mp4",'-i',os.path.join(archRepoDir,startObj,startObj + ".wav"),'-t','00:00:10.0',"-vf","drawtext=fontfile='C\\:/Windows/Fonts/Arial.ttf':textfile=" + txtfile + ":fontcolor=white:fontsize=24:x=(w-tw)/2:y=(h/PHI)+th",'-acodec','libmp3lame','-b:a','320k','-ar','48000','-vcodec','libx264','-preset','slow','-crf','20','-shortest',"headtxt.mp4"])
		subprocess.call(['ffmpeg','-loop','1','-i',os.path.join(archRepoDir,startObj,startObj + ".jpg"),'-i',os.path.join(archRepoDir,startObj,startObj + ".wav"),'-ss','00:00:05.00','-acodec','libmp3lame','-b:a','320k','-ar','48000','-vcodec','libx264','-preset','slow','-crf','20','-shortest',"tail.mp4"])

def main():
	#initialize a buncha crap
	parser = argparse.ArgumentParser(description="Makes a broadcast-ready file from a single input file")
	parser.add_argument('-i','--input',dest='i',help='the canonical name of the disc to make a vid for, e.g. cusb_victor_123_04_567_89')
	args = parser.parse_args()
	#init stuff from our config file
	config = ConfigParser.ConfigParser()
	config.read("C:/Users/" + getpass.getuser() + "/microservices-config.ini")
	archRepoDir = config.get('discs','archRepoDir')
	bextsDir = config.get('discs','mtdCaptures')
	mmrepo = config.get('global','scriptRepo')
	
	makeIt(args.i,archRepoDir)
	
	
dependencies()
main()