#!/usr/bin/env python

import os
import subprocess
import sys
import glob
import re
import argparse
import imp
import getpass
from distutils import spawn

#check that we have required software installed
def dependencies():
	depends = ['ffmpeg','ffprobe']
	for d in depends:
		if spawn.find_executable(d) is None:
			print "Buddy, you gotta install " + d
			sys.exit()
	return

def makeThem(startObj, archRepoDir,vidLeadDir):	
	###INIT VARS###
	txtfile = os.path.join(archRepoDir,startObj,startObj + "yt.txt")
	txtfile = txtfile.replace("\\","/")
	if not os.path.exists(txtfile):
		print "The text file with descriptive info from DAHR does not exist"
		print "Please write one and save it as " + startObj + "yt.txt in " + os.path.dirname(txtfile)
		sys.exit()
	txtfile = txtfile.replace(":","\\\:")
	qa = '"' + "'"
	aq = "'" + '"'
	###END INIT###
	with ut.cd(os.path.join(archRepoDir,startObj)):
		
		#headwhite.mov
		#make a blank white 1920x1080 frame 10s long
		#subprocess.call(['ffmpeg','-f','lavfi','-i','color=c=white:s=1920x1080:d=10','-c:v','prores','-profile:v','3','-qscale:v','4','headwhite.mov'])
		
		#headlogo.mov
		#overlay the library logo onto this blank white 1920x1080 10s frame, but make this vid 5s
		#text above logo that says "From the collections of the" same size as following descriptive text
		#subprocess.call(['ffmpeg','-i','headwhite.mov','-i',"S:/avlab/ucsb-lib-logo.jpg",'-f','lavfi','-i','anullsrc=channel_layout=mono:sample_rate=48000','-filter_complex','[1:v]scale=528x101 [ovrl],[0:v][ovrl] overlay=260:600','-t','5','-c:v','prores','-profile:v','3','-qscale:v','4','-c:a','aac','-b:a','320k','headlogo.mov'])
		
		#headtxt.mov
		#overlay the descriptive metadata from our yt.txt file onto this blank white 1920x1080 10s frame
		subprocess.call(['ffmpeg','-i',os.path.join(vidLeadDir,"headwhite.mov"),"-vf","drawtext=fontfile='C\\:/Windows/Fonts/Arial.ttf':textfile=" + txtfile + ":fontcolor=black:fontsize=60:x=(w-tw)/2:y=540",'-c:v','prores','-profile:v','3','-qscale:v','4','-shortest','-threads','0',"headtxt.mov"])
		
		#labelimg.png
		#scale the tif image of our disc label to fit the 1920x1080 frame
		subprocess.call(['ffmpeg','-i',startObj + ".jpg",'-vf',"scale='if(gt(a,16/9),1920,-1)':'if(gt(a,16/9),-1,1080)'",'labelimg.png'])
		
		#tail.mov
		#write a 5minute soundless video file of the scaled disc label image, pad the sides of the 1080x1080 input png of the disc label
		subprocess.call(['ffmpeg','-loop','1','-i','labelimg.png','-t','300','-vf','pad=1920:1080:420:0:black','-c:v','prores','-profile:v','3','-qscale:v','4','-s','1920x1080','-threads','0',"tail.mov"])
		
		#headtail.mov
		#concatenate the descriptive frames with the soundless disc label image frames, putting a cross dissolve between them
		subprocess.call(['ffmpeg','-i','headtxt.mov','-i','tail.mov','-filter_complex','color=white:1920x1080:d=305[base];[0:v]setpts=PTS-STARTPTS[v0];[1:v]format=yuv422p10le,fade=in:st=0:d=2:alpha=1,setpts=PTS-STARTPTS+((8)/TB)[v1];[base][v0]overlay[tmp];[tmp][v1]overlay,format=yuv422p10le[fv]','-c:v','prores','-profile:v','3','-qscale:v','4','-map','[fv]','-threads','0','headtail.mov'])
		
		#headtailwithaudio.mov
		#pop the audio into the concatenated vid
		subprocess.call(['ffmpeg','-i','headtail.mov','-i',startObj + ".wav",'-c:v','copy','-c:a','aac','-ar','48000','-b:a','128k','-shortest','-threads','0','headtailwithaudio.mov'])

		
def concatThem(startObj, archRepoDir,vidLeadDir):
	with ut.cd(os.path.join(archRepoDir,startObj)):
		###INIT CONCAT.TXT###
		concatxt = open("concat.txt","w")
		concatxt.write('file ' + os.path.join(vidLeadDir,'headlogoandtxt.mov\n'))
		concatxt.write('file headtailwithaudio.mov\n')
		concatxt.close()
		###END INIT###
		
		#actually concatenate the headlogo with the headtailwithaudio file
		subprocess.call(['ffmpeg','-f','concat','-safe','0','-i','concat.txt','-c','copy', os.path.basename(startObj) + "yt.mov"])
		#create an mp4 from that, pretty visually compressed
		subprocess.call(['ffmpeg','-i',os.path.basename(startObj) + "yt.mov",'-pix_fmt','yuv420p','-c:v','libx264','-crf','28','-c:a','copy','-movflags','faststart','-maxrate','4380k','-threads','0',os.path.basename(startObj) + "yt.mp4"])
		
		#remove all the crap we created
		os.remove(os.path.join(archRepoDir,startObj,'concat.txt'))
		#os.remove(os.path.join(archRepoDir,startObj,'headwhite.mov'))
		os.remove(os.path.join(archRepoDir,startObj,'headtxt.mov'))
		os.remove(os.path.join(archRepoDir,startObj,'tail.mov'))
		os.remove(os.path.join(archRepoDir,startObj,'headtail.mov'))
		os.remove(os.path.join(archRepoDir,startObj,'headtailwithaudio.mov'))
		#os.remove(os.path.join(archRepoDir,startObj,startObj + "yt.txt")		
		
def main():
	###INIT VARS###
	dn, fn = os.path.split(os.path.abspath(__file__))
	global conf
	rawconfig = imp.load_source('config',os.path.join(dn,'config.py'))
	conf = rawconfig.config()
	global ut
	ut = imp.load_source("util",os.path.join(dn,"util.py"))
	global log
	log = imp.load_source('log',os.path.join(dn,'logger.py'))
	parser = argparse.ArgumentParser(description="Makes a broadcast-ready file from a single input file")
	parser.add_argument('-so','--startObject',dest='i',help='the canonical name of the disc to make a vid for, e.g. cusb_victor_123_04_567_89')
	parser.add_argument('-d','--disc',dest='d',action='store_true',default=False,help='make a video for a disc. cylinder option coming soon')
	args = parser.parse_args()
	archRepoDir = conf.discs.archRepoDir
	vidLeadDir = conf.video.vid_leads
	###END INIT###
	if args.d is True:
		makeThem(args.so,archRepoDir,vidLeadDir)
		concatThem(args.so,archRepoDir,vidLeadDir)
	
dependencies()
main()