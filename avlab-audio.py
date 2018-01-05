#!/usr/bin/env python
'''
processes raw transfers of magnetic tape
'''

import argparse
import getpass
import os
import subprocess
import csv
import re
import ast
import time
import sys
import pyodbc
###UCSB modules###
import config as rawconfig
import util as ut
import logger as log
import mtd
import makestartobject as makeso
import ff



def move(kwargs):
	'''
	moves processed folder and raw transfer to repo directory
	'''
	print "moving " + kwargs.aNumber
	endDirThousand = ut.make_endDirThousand(kwargs.aNumber) #input arg here is a1234 but we want just the number
	kwargs.endDir = os.path.join(conf.magneticTape.repo,endDirThousand,kwargs.aNumber.lower())
	#hashmove it and grip the output so we can delete the raw files YEAHHH BOY
	output = subprocess.Popen([conf.python,os.path.join(conf.scriptRepo,'hashmove.py'),kwargs.processDir,kwargs.endDir],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	foo,err = output.communicate()
	print foo
	sourcehash = re.search('srce\s\S+\s\w{32}',foo)
	desthash = re.search('dest\s\S+\s\w{32}',foo)
	dh = desthash.group()
	sh = sourcehash.group()
	if sh[-32:] == dh[-32:]:
		output = subprocess.Popen([conf.python,os.path.join(conf.scriptRepo,'hashmove.py'),os.path.join(conf.magneticTape.new_ingest,kwargs.rawcapNumber + ".wav"),kwargs.endDir],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		foo,err = output.communicate()
		print foo

def mono_silence(kwargs):
	'''
	runs silence remove on mono files
	ffmpeg -af silenceremove works on the file level, not stream level
	'''
	with ut.cd(kwargs.processDir):
		for f in os.listdir(os.getcwd()):#make a list of the whole directory contents
			if f.endswith(".wav"):#grip just wavs
				kwargs.filename = f
				print kwargs.filename
				full_ffstr = ff.prefix(f) + ff.audio_secondary_ffproc(conf,kwargs)
				returncode = ff.go(full_ffstr)
				if returncode is not True:
					print "There was a problem processing " + kwargs.aNumber
					return False
				else:
					os.remove(f)
					os.rename(f.replace(".wav","-silenced.wav"),f)
					return True

def reverse(ffproc,kwargs):
	'''
	runs makereverse on files that need it
	'''
	iofile = make_iofile(ffproc,kwargs,"revface")
	try:
		output = subprocess.check_output([conf.python,os.path.join(conf.scriptRepo,'makereverse.py'),'-i',iofile])
		rtncode = True
	except subprocess.CalledProcessError,e:
		rtncode = e.returncode
	return rtncode

def make_iofile(ffproc,kwargs,process):
	'''
	generates a filename for the output files for reverse, halfspeed, doublespeed processes
	'''
	filenames = ['filename0','filename1']
	iofile = ''
	print ffproc
	if process == 'revface':
		face = ffproc.revface[1]
	elif process == 'hlvface' or process == 'dblface':
		if ffproc.hlvface:
			face = ffproc.hlvface[1]
		elif ffproc.dblface:
			face = ffproc.dblface[1]
	for f in filenames:
		if f in ffproc:
			if face in ffproc[f]:
				iofile = os.path.join(kwargs.processDir,ffproc[f])
	if not iofile:
		for f in os.listdir(kwargs.processDir):
			if f == 'cusb-'+ kwargs.aNumber.lower() + "a.wav":
				iofile = os.path.join(kwargs.processDir,'cusb-'+kwargs.aNumber.lower() + "a.wav")
	if not iofile:
		print "There was a filename mismatch between the face selected to reverse and the files available to be reversed"
		print ""
		return None
	else:
		return iofile

def sampleratenormalize(ffproc,kwargs):
	'''
	normalizes the sample rate to 96kHz for files which have had a speed change
	'''
	iofile = make_iofile(ffproc,kwargs,"hlvface")
	kwargs.filename = os.path.join(kwargs.processDir,iofile)
	full_ffstr = ff.sampleratenormalize(conf,kwargs)
	returncode = ff.go(full_ffstr)
	if returncode is not True:
		print "There was a problem processing " + kwargs.aNumber
		return False
	else:
		os.remove(kwargs.filename)
		os.rename(kwargs.filename.replace(".wav","-resampled.wav"),kwargs.filename)
		return True


def makebext(aNumber,processDir):
	'''
	embed bext metadata in processed file(s)
	'''
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

def size_check(kwargs):
	'''
	verifies that file to be processed is not larger than 4GB
	4GB is the largest valid filesize for wave spec
	'''
	size = os.path.getsize(os.path.join(conf.magneticTape.new_ingest,kwargs.rawcapNumber+ ".wav"))
	if size >= 4294967296:
		return True
	else:
		return False

def process(kwargs):
	'''
	directs the processing of a file
	'''
	#check if it's bigger than WAVE spec
	tooBig = size_check(kwargs)
	if tooBig is True:
		print "this file is too large to process with ffmpeg"
		return False
	#get the aNumber, channelConfig, face of the file
	acf = mtd.get_aNumber_channelConfig_face(conf.magneticTape.cnxn,**kwargs)
	print acf
	#verify that we got an object back from mtd.py
	if acf is None:
		return False
	else:
		#verify that FM record filled out compeltely
		processNone = 0
		for p in acf:
			if acf[p] is None:
				processNone = 1
				return False
		if processNone > 0:
			print ""
			print "ERROR - FileMaker record incomplete"
			print "Please check FileMaker record for rawcapture:"
			print args.i
			return False
		#add aNumber, channelConfig, face info to kwargs
		for k,v in acf.iteritems():
			kwargs[k] = v
		kwargs = ut.dotdict(kwargs)
		#verify that there's not two channelConfigs set in FM
		if "\r" in kwargs.channelConfig:
			return False
		kwargs.aNumber = "a" + kwargs.aNumber
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
		if not ffWorked:
			return False
		#special add for mono files
		if not "Stereo" in kwargs.channelConfig and not "Cassette" in kwargs.channelConfig:
			ffWorked = mono_silence(kwargs)
		#if we need to reverse do it
		if ffproc.revface:
			revWorked = reverse(ffproc,kwargs)
			if revWorked is not True:
				print "there was a problem reversing the file"
				print revWorked
				return False
		#if we need to normalize our sample rate to 96kHz, because we sped up or slowed down a recording, do it here
		if ffproc.hlvface or ffproc.dblface:
			print "sample rate normalize"
			srnWorked = sampleratenormalize(ffproc,kwargs)
			if not srnWorked:
				print "there was a problem normalizing the sampel rate of the file"
				return False
		#embed bext info
		makebext(kwargs.aNumber,kwargs.processDir)
		#hashmove them to the repo dir
		move(kwargs)
		return True

def main():
	'''
	do the thing
	'''
	global conf
	conf = rawconfig.config()
	parser = argparse.ArgumentParser(description="processes magnetic tape transfers")
	parser.add_argument('-m',dest='m',choices=['batch','single'],default=False,help='mode, for processing a single transfer or a batch in new_ingest')
	parser.add_argument('-i','--input',dest='i',help="the rawcapture file.wav to process, single mode only")
	args = parser.parse_args()

	###SINGLE MODE###
	if args.m == 'single':
		###INIT###
		file = args.i
		rawfname,ext = os.path.splitext(file)
		###END INIT###
		###GET ANUMBER FACE AND CHANNELCONFIG FROM FILEMAKER###
		#output = subprocess.check_output(["python","fm-stuff.py","-pi","-t","-p","nameFormat","-i",rawfname]) #get aNumber, channelconfig, face from FileMaker
		kwargs = ut.dotdict({"rawcapNumber":args.i})
		processWorked = process(kwargs)
		if processWorked is not True:
			print "there was an error processing that file"
	###END SINGLE MODE###
	###BATCH MODE###
	elif args.m == 'batch':
		for dirs,subdirs,files in os.walk(conf.magneticTape.new_ingest):
			for file in files:
				###GET RID OF BS###
				if file.endswith(".gpk") or file.endswith(".mrk") or file.endswith(".bak") or file.endswith(".pkf"):
					try:
						os.remove(file)
					except:
						pass
				###END BS###
				###PROCESS CAPTURE###
				elif os.path.exists(os.path.join(conf.magneticTape.new_ingest,file)) and file.endswith(".wav"):
					try: #control for files currently in use
						subprocess.call("ffprobe " + os.path.join(dirs,file))
					except:
						continue
					###INIT###
					print file
					rawfname,ext = os.path.splitext(file)
					###END INIT###
					###GET ANUMBER FACE AND CHANNELCONFIG FROM FILEMAKER###
					kwargs = ut.dotdict({"rawcapNumber":rawfname})
					processWorked = process(kwargs)
					if not processWorked:
						continue
				###END PROCESS CAPTURE###
	###END BATCH MODE###
if __name__ == '__main__':
	main()
