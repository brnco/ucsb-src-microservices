#!/usr/bin/env python

import os
import subprocess
import argparse
import re
import time
import sys
sys.path.insert(0,"S:/avlab/microservices")
#remove ^ in production
###UCSB modules###
import config as rawconfig
conf = rawconfig.config()
import util as ut
import logger as log
import mtd
import makestartobject as makeso
import ff

def makebext(aNumber,processDir): #embed bext info using bwfmetaedit
	try:
		kwargs = {"aNumber":aNumber,"bextVersion":"1"}
		bextstr = mtd.makebext_complete(pyodbc.connect(conf.magneticTape.cnxn),**kwargs)
	except:
		bextstr = "--originator=US,CUSB,SRC --originatorReference=" + aNumber.capitalize()
	with ut.cd(processDir):
		for f in os.listdir(os.getcwd()):
			if f.endswith(".wav"):
				subprocess.check_output("bwfmetaedit --in-core-remove " + f) #removes all bext info currently present
				print "embedding MD5 hash of data chunk..."
				subprocess.check_output("bwfmetaedit --MD5-Embed-Overwrite " + f) #embeds md5 hash of data chunk, overwrites if currently exists
				print "embedding BEXT chunk..."
				subprocess.check_output("bwfmetaedit " + bextstr + " " + f) #embeds bext v0 info

def process(thefile):
	print thefile.rawcapNumber
	kwargs = thefile
	acf = mtd.get_aNumber_channelConfig_face(conf.magneticTape.cnxn,**kwargs)
	print acf
	if acf is not None:
		for k,v in acf.iteritems():
			kwargs[k] = v
		kwargs = ut.dotdict(kwargs)
		kwargs.aNumber = "a" + kwargs.aNumber
		###END GET ANUMBER FACE CHANNELCONFIG FROM FILEMAKER###
		###DO THE FFMPEG###
		#init folder to do the work in
		kwargs.processDir = os.path.join(conf.magneticTape.new_ingest,kwargs.aNumber)
		if not os.path.exists(kwargs.processDir):
			os.makedirs(kwargs.processDir)
			time.sleep(1)
		#make the full ffstr using the paths we have
		ffproc = ff.audio_init_ffproc(conf,kwargs)
		full_ffstr = ff.prefix(os.path.join(conf.magneticTape.new_ingest,kwargs.rawcapNumber) + "." + conf.ffmpeg.acodec_master_format) + ffproc.ff_suffix
		print full_ffstr
		#run ffmpeg on the file and make sure it completes successfully
		with ut.cd(kwargs.processDir):
			ffWorked = ff.go(full_ffstr)
		makebext(kwargs.aNumber,kwargs.processDir)

def main():
	for dirs, subdirs, files, in os.walk(sys.argv[1]):
		for f in files:
			thefile = ut.dotdict({})
			thefile.fnamext = f
			thefile.rawcapNumber, thefile.ext = os.path.splitext(f)
			thefile.fullpath = os.path.join(dirs, f)
			if thefile.ext == '.md5':
				continue
			elif thefile.ext == '.wav':
				process(thefile)

if __name__ == '__main__':
	main()
