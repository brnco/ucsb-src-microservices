#!/usr/bin/env python
'''
makemp3
does the best that it can
takes 1 argument for object to convert to mp3
keeps input channel config
outputs 320k mp3
still gotta add png support for album covers?
'''
import os
import subprocess
import sys
import glob
import re
import argparse
import time
###UCSB modules###
import config as rawconfig
import util as ut
#import logger as log
import mtd
import ff
import makestartobject as makeso

def make_video(thefile):
	'''
	actually use everything we've made to make the mp4
	'''
	with ut.cd(thefile.dir):
		if thefile.ext == 'mxf':
			ffstr = 'ffmpeg -i ' + thefile.infullpath + ' -map 0 -dn -vf "weave,setfield=bff,setdar=4/3" -c:v libx264 -preset slower -crf 18 -c:a aac ' + thefile.outfullpath
		else:
			ffstr = 'ffmpeg -i ' + thefile.infullpath + ' -map 0 -dn -c:v libx264 -preset slower -crf 18 -c:a aac ' + thefile.outfullpath
		print ffstr
		ffWorked = ff.go(ffstr)
		if ffWorked is not True:
			print "makeaccess encountered an error transcoding that file"
			print ffWorked

def make_audio(thefile, mtdstr):	#make the mp3
	'''
	actually use everything we've configured so far to make an mp3
	'''
	with ut.cd(thefile.dir):
		if mtdstr:
			ffstr = 'ffmpeg -i ' + thefile.infullpath + ' ' + mtdstr + ' -ar ' + conf.ffmpeg.acodec_access_arate + \
			' -ab ' + conf.ffmpeg.acodec_access_bitrate + ' -f mp3 ' + conf.ffmpeg.acodec_writeid3 + ' -y ' + thefile.outfullpath
			#subprocess.call(['ffmpeg','-f','ffmetadata','-i',mtdObj,'-i',startObj,'-ar','44100','-ab','320k','-f','mp3','-id3v2_version','3','-write_id3v1','1','-y',endObj], shell=True) #atually do it
		else:
			ffstr = 'ffmpeg -i ' + thefile.infullpath + ' -ar ' + conf.ffmpeg.acodec_access_arate + \
			' -ab ' + conf.ffmpeg.acodec_access_bitrate + ' -f mp3 ' + conf.ffmpeg.acodec_writeid3 + ' -y ' + thefile.outfullpath
			#subprocess.call(['ffmpeg','-i',startObj,'-ar','44100','-ab','320k','-f','mp3','-id3v2_version','3','-write_id3v1','1','-y',endObj]) #atually do it
		print ffstr
		ffWorked = ff.go(ffstr)
		if ffWorked is not True:
			print "makeaccess encountered an error transcoding that file"
			print ffWorked

def parse_input(args):
	'''
	returns dictionary of file attributes
	'''
	thefile = ut.dotdict({})
	startObj = subprocess.check_output(['python',os.path.join(conf.scriptRepo,'makestartobject.py'),'-i',args.i])
	thefile.infullpath = startObj.replace("\\",'/').strip() #for the windows peeps
	thefile.fname, thefile.ext = os.path.splitext(os.path.basename(os.path.abspath(thefile.infullpath)))
	thefile.startUseChar = thefile.fname[-1:] #grabs the last char of file name which is ~sometimes~ the use character
	thefile.dir = os.path.dirname(thefile.infullpath) #grabs the directory that this object is in (we'll cd into it later)
	if "v" in args.i:
		thefile.outfname = thefile.fname.replace("-pres","").replace("-broadcast","") + "-acc." + conf.ffmpeg.vcodec_access_format
	else:
		thefile = make_endUseChar(thefile) #grip the right filename endings, canonical name of the asset
		thefile.outfname = thefile.assetName + thefile.endUseChar + "." + conf.ffmpeg.acodec_access_format
	thefile.outfullpath = os.path.join(thefile.dir, thefile.outfname)
	return thefile

def make_endUseChar(thefile):
	'''
	end use characters correspond to different parts of our OAIS implementation
	filenames ending in "a" are our archival masters
	filenames ending in "b" are our broadcast masters
	filenames ending in "c" are intermediate files
	filenames ending in "d" are access files
	'''
	se = {"a":"d", "b":"d", "c":"d", "m":''} #start:end character rules
	thefile.endUseChar = ''
	for s in se:
		if thefile.startUseChar == s:
			thefile.endUseChar = se[s]
			thefile.assetName = thefile.fname[:-1]
			return thefile
	if not thefile.endUseChar:
		thefile.endUseChar = 'd'
		thefile.assetName = thefile.fname
		return thefile

def main():
	'''
	do the thing
	'''
	global conf
	conf = rawconfig.config()
	parser = argparse.ArgumentParser(description="Makes an mp3 with ID3 tags")
	parser.add_argument('-i', '--input', dest='i', help='the file to be transcoded')
	parser.add_argument('-o', '--output', dest='o', choices=['mp3','mp4'], help='the output format')
	args = parser.parse_args() #create a dictionary instead of leaving args in NAMESPACE land
	thefile = parse_input(args)
	if args.o is 'mp3':
		mtdstr = mtd.make_manualid3(thefile) #call the id3 check function
		make_audio(thefile, mtdstr) #call the makeaudio function
	else:
		if thefile.ext == '.mp4':
			print "file is already in our access format"
		else:
			make_video(thefile)

if __name__ == '__main__':
	main()
