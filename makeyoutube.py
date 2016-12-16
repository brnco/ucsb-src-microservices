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

def makeThem(startObj, archRepoDir):	
	txtfile = os.path.join(archRepoDir,startObj,startObj + "yt.txt")
	txtfile = txtfile.replace("\\","/")
	txtfile = txtfile.replace(":","\\\:")
	if not os.path.exists(txtfile):
		print "The text file with descriptive info from DAHR does not exist"
		print "Please write one and save it as " + startObj + ".yt.txt in " + os.path.dirname(txtfile)
		sys.exit()
	qa = '"' + "'"
	aq = "'" + '"'
	with cd(os.path.join(archRepoDir,startObj)):
		
		#headwhite.mov
		#make a blank white 1920x1080 frame 10s long
		#subprocess.call(['ffmpeg','-f','lavfi','-i','color=c=white:s=1920x1080:d=10','-c:v','prores','-profile:v','3','-qscale:v','4',"headwhite.mov"])
		
		#headlogo.mov
		#overlay the library logo onto this blank white 1920x1080 10s frame, but make this vid 5s
		#logo 100% larger, centered
		#text above logo that says "From the collections of the" same size as following descriptive text
		#subprocess.call(['ffmpeg','-i','headwhite.mov','-i',"S:/avlab/ucsb-lib-logo.jpg",'-f','lavfi','-i','anullsrc=channel_layout=mono:sample_rate=48000','-filter_complex','[1:v]scale=528x101 [ovrl],[0:v][ovrl] overlay=260:600','-t','5','-c:v','prores','-profile:v','3','-qscale:v','4','-c:a','aac','-b:a','320k','headlogo.mov'])
		
		#headtxt.mov
		#overlay the descriptive metadata from our yt.txt file onto this blank white 1920x1080 10s frame
		#make text 100% larger
		subprocess.call(['ffmpeg','-i',"R:/78rpm/avlab/projects/video-files/headwhite.mov","-vf","drawtext=fontfile='C\\:/Windows/Fonts/Arial.ttf':textfile=" + txtfile + ":fontcolor=black:fontsize=40:x=(w-tw)/2:y=(h/PHI)+th",'-c:v','prores','-profile:v','3','-qscale:v','4','-shortest',"headtxt.mov"])
		
		#labelimg.png
		#scale the tif image of our disc label to fit the 1920x1080 frame
		subprocess.call(['ffmpeg','-i',startObj + ".jpg",'-vf',"scale='if(gt(a,16/9),1920,-1)':'if(gt(a,16/9),-1,1080)'",'labelimg.png'])
		
		#tail.mov
		#write a 5minute soundless video file of the scaled disc label image, pad the sides of the 1080x1080 input png of the disc label
		subprocess.call(['ffmpeg','-loop','1','-i','labelimg.png','-t','300','-vf','pad=1920:1080:420:0:black','-c:v','prores','-profile:v','3','-qscale:v','4','-s','1920x1080',"tail.mov"])
		
		#headtail.mov
		#concatenate the descriptive frames with the soundless disc label image frames, putting a cross dissolve between them
		subprocess.call(['ffmpeg','-i','headtxt.mov','-i','tail.mov','-filter_complex','color=white:1920x1080:d=305[base];[0:v]setpts=PTS-STARTPTS[v0];[1:v]format=yuv422p10le,fade=in:st=0:d=2:alpha=1,setpts=PTS-STARTPTS+((8)/TB)[v1];[base][v0]overlay[tmp];[tmp][v1]overlay,format=yuv422p10le[fv]','-c:v','prores','-profile:v','3','-qscale:v','4','-map','[fv]','headtail.mov'])
		
		#headtailwithaudio.mov
		#pop the audio into the concatenated vid
		subprocess.call(['ffmpeg','-i','headtail.mov','-i',startObj + ".wav",'-c:v','copy','-c:a','aac','-ar','48000','-b:a','320k','-shortest','headtailwithaudio.mov'])

		
def concatThem(startObj, archRepoDir):
	with cd(os.path.join(archRepoDir,startObj)):
		concatxt = open("concat.txt","w")
		concatxt.write('file R:/78rpm/avlab/projects/video-files/headlogoandtxt.mov\n')
		concatxt.write('file headtailwithaudio.mov\n')
		concatxt.close()
		
		#actually concatenate the headlogo with the headtailwithaudio file
		subprocess.call(['ffmpeg','-f','concat','-i','concat.txt','-c','copy', os.path.basename(startObj) + "yt.mov"])
		#create and mp4 from that, pretty visually compressed
		subprocess.call(['ffmpeg','-i',os.path.basename(startObj) + "yt.mov",'-pix_fmt','yuv420p','-c:v','libx264','-preset','slow','-crf','28','-c:a','copy',os.path.basename(startObj) + "yt.mp4"])
		
		#remove all the crap we created
		os.remove(os.path.join(archRepoDir,startObj,'concat.txt'))
		#os.remove(os.path.join(archRepoDir,startObj,'headwhite.mov'))
		os.remove(os.path.join(archRepoDir,startObj,'headtxt.mov'))
		os.remove(os.path.join(archRepoDir,startObj,'tail.mov'))
		os.remove(os.path.join(archRepoDir,startObj,'headtail.mov'))
		os.remove(os.path.join(archRepoDir,startObj,'headtailwithaudio.mov'))
		#os.remove(os.path.join(archRepoDir,startObj,startObj + "yt.txt")		
		
def main():
	#initialize a buncha crap
	parser = argparse.ArgumentParser(description="Makes a broadcast-ready file from a single input file")
	parser.add_argument('-i','--input',dest='i',help='the canonical name of the disc to make a vid for, e.g. cusb_victor_123_04_567_89')
	parser.add_argument('-d','--disc',dest='d',action='store_true',default=False,help='make a video for a disc. cylinder option coming soon')
	args = parser.parse_args()
	#init stuff from our config file
	config = ConfigParser.ConfigParser()
	config.read("C:/Users/" + getpass.getuser() + "/microservices-config.ini")
	archRepoDir = config.get('discs','archRepoDir')
	mmrepo = config.get('global','scriptRepo')
	if args.d is True:
		makeThem(args.i,archRepoDir)
		concatThem(args.i,archRepoDir)
	
dependencies()
main()