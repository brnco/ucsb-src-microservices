#!/usr/bin/env python

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


#hashmove processing folder to the repo	
def move(rawfname,aNumber,captureDir,archRepoDir):
	if aNumber.endswith("A") or aNumber.endswith("B") or aNumber.endswith("C") or aNumber.endswith("D"):
		aNumber = aNumber[:-1]
	dirNumber = aNumber
	processingDir = os.path.join(captureDir,dirNumber)
	if os.path.isdir(processingDir):
		endDirThousand = aNumber.replace("a","") #input arg here is a1234 but we want just the number
		#the following separates out the first digit and assigns an appropriate number of zeroes to match our dir structure
		if len(endDirThousand) < 5:
			endDirThousand = endDirThousand[:1] + "000"
		else:
			endDirThousand = endDirThousand[:2] + "000"
		endDir = os.path.join(archRepoDir,endDirThousand,dirNumber)
		#hashmove it and grip the output so we can delete the raw files YEAHHH BOY
		output = subprocess.Popen(['python',os.path.join(conf.scriptRepo,'hashmove.py'),processingDir,endDir],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		foo,err = output.communicate()
		print foo
		sourcehash = re.search('srce\s\S+\s\w{32}',foo)
		desthash = re.search('dest\s\S+\s\w{32}',foo)
		dh = desthash.group()
		sh = sourcehash.group()
		if sh[-32:] == dh[-32:]:
			output = subprocess.Popen(['python',os.path.join(conf.scriptRepo,'hashmove.py'),os.path.join(captureDir,rawfname + ".wav"),endDir],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
			foo,err = output.communicate()
			print foo

	
def ffprocess(full_ffstr,processDir): #actually process with ffmpeg
	if not os.path.exists(processDir):
		os.makedirs(processDir) #actually make the processing directory
	time.sleep(1) #give the file table time to catch up
	###DO THE THING###
	with ut.cd(processDir):
		rtncode = ff.go(full_ffstr)
		if rtncode > 0:
			print "There was a problem processing " + os.path.basename(processDir)
			return False
	return True		
	###END DOING THE THING###


#def mono_silence(rawfname,face,aNumber,processDir): #silence removal for tapes that are mono
def mono_silence(kwargs):
	#ffmpeg -af silenceremove works on the file level, not stream level
	with ut.cd(kwargs.processDir):
		for f in os.listdir(os.getcwd()):#make a list of the whole directory contents
			if f.endswith(".wav"):#grip just wavs
				kwargs['filename'] = f
				full_ffstr = ff.prefix(f) + ff.audio_secondary_ffproc(**kwargs)
				returncode = ff.go(full_ffstr)
				if returncode > 0:
					print "There was a problem processing " + kwargs.aNumber
					return False
				else:
					os.remove(f)
					os.rename(f.replace(".wav","-silenced.wav"),f)
	return True				
	'''try:
		#silencedetect filter arguments are same order as on ffmpeg filters doc
		returncode = subprocess.check_output("ffmpeg -i " + f + " -af silenceremove=1:0:-50dB:1:30:-50dB -c:a pcm_s24le -map 0 -threads 0 " + f.replace(".wav","") + "-silenced.wav")
		#CHECK_OUTPUT IS THE BEST
		returncode = 0
	except subprocess.CalledProcessError,e: #if there's an error, set the returncode to that
		returncode = e.returncode
	if returncode < 1: #if the returncode is not an error, we know that ffmepg was sucessful and that it's safe to delete the start file
		os.remove(os.path.join(processDir,f))
		os.rename(os.path.join(processDir,f.replace(".wav","-silenced.wav")),f)'''
	#NOTE FOR LATER
	#NEED TO RETURN THE RETURNCODE TO MAIN()
	

def reverse(rawfname,face,aNumber,channelConfig,processDir):#calls makereverse
	###INIT VARS###
	revface = subprocess.check_output(["python","fm-stuff.py","-pi","-t","-p","reverse","-i",rawfname,"-f",face,"-cc",channelConfig])
	###END INIT###
	###REVERSE FACE###
	if "fA" in revface and not "fAB" in revface:
		if os.path.exists(os.path.join(processDir,"cusb-" + aNumber + "Aa.wav")):
			subprocess.check_output(['python',os.path.join(conf.scriptRepo,"makereverse.py"),'-i',os.path.join(processDir,"cusb-" + aNumber + "Aa.wav")])
	elif "fC" in revface and not "fCD" in revface:
		if os.path.exists(os.path.join(processDir,"cusb-" + aNumber + "Ca.wav")):	
			subprocess.check_output(['python',os.path.join(conf.scriptRepo,"makereverse.py"),'-i',os.path.join(processDir,"cusb-" + aNumber + "Ca.wav")])	
	elif "fB" in revface:
		if os.path.exists(os.path.join(processDir,"cusb-" + aNumber + "Ba.wav")):	
			subprocess.check_output(['python',os.path.join(conf.scriptRepo,"makereverse.py"),'-i',os.path.join(processDir,"cusb-" + aNumber + "Ba.wav")])
	elif "fD" in revface:
		if os.path.exists(os.path.join(processDir,"cusb-" + aNumber + "Da.wav")):	
			subprocess.check_output(['python',os.path.join(conf.scriptRepo,"makereverse.py"),'-i',os.path.join(processDir,"cusb-" + aNumber + "Da.wav")])
	elif "fAB" in revface:
		if os.path.exists(os.path.join(processDir,"cusb-" + aNumber + "Aa.wav")):
			subprocess.check_output(['python',os.path.join(conf.scriptRepo,"makereverse.py"),'-i',os.path.join(processDir,"cusb-" + aNumber + "Aa.wav")])
		if os.path.exists(os.path.join(processDir,"cusb-" + aNumber + "Ba.wav")):
			subprocess.check_output(['python',os.path.join(conf.scriptRepo,"makereverse.py"),'-i',os.path.join(processDir,"cusb-" + aNumber + "Ba.wav")])
		#sometimes the face isn't specified in the filename
		elif os.path.exists(os.path.join(processDir,"cusb-" + aNumber + "a.wav")):
			print "2"
			subprocess.check_output(['python',os.path.join(conf.scriptRepo,"makereverse.py"),'-i',os.path.join(processDir,"cusb-" + aNumber + "a.wav")])
	elif "fCD" in revface:
		if os.path.exists(os.path.join(processDir,"cusb-" + aNumber + "Ca.wav")):
			subprocess.check_output(['python',os.path.join(conf.scriptRepo,"makereverse.py"),'-i',os.path.join(processDir,"cusb-" + aNumber + "Ca.wav")])
	###END REVERSE FACE###

	
def sampleratenormalize(processDir):
	#ok so by now every file in the processing dir is the correct channel config & plays in correct direction BUT
	#we need to normalize to 96kHz
	#files with speed changes are currently set to 192000Hz or 48000Hz
	with ut.cd(processDir):
		for f in os.listdir(os.getcwd()): #for each file in the processing dir
			if f.endswith(".wav"):
				print "ffprobe and resample if necessary"
				#send ffprobe output to output.communicate()
				output = subprocess.Popen("ffprobe -show_streams -of flat " + f,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
				ffdata,err = output.communicate()
				###GET SAMPLE RATE###
				match = ''
				sr = ''
				match = re.search(r".*sample_rate=.*",ffdata)
				if match:
					_sr = match.group().split('"')[1::2]
					sr = _sr[0]
				###END GET SAMPLE RATE###
				###CONVERT SAMPLE RATE###
				if not sr == "96000":
					output = subprocess.call("ffmpeg -i " + f + " -ar 96000 -c:a pcm_s24le " + f.replace(".wav","") + "-resampled.wav")
					if os.path.getsize(f.replace(".wav","") + "-resampled.wav") > 50000:
						os.remove(os.path.join(os.getcwd(),f))
						time.sleep(1)
						os.rename(f.replace(".wav","") + "-resampled.wav",f) 
				###END CONVERT###

	
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

def process(kwargs):
	acf = mtd.get_aNumber_channelConfig_face(conf.magneticTape.cnxn,**kwargs)
	print acf
	if acf is not None:
		processNone = 0
		for p in acf:
			if acf[p] is None:
				processNone = 1
				break
		if processNone > 0:
			print ""
			print "ERROR - FileMaker record incomplete"
			print "Please check FileMaker record for rawcapture:"
			print args.i
			sys.exit()
		for k,v in acf.iteritems():
			kwargs[k] = v
		kwargs = ut.dotdict(kwargs)
		kwargs.aNumber = "a" + kwargs.aNumber
		###END GET ANUMBER FACE CHANNELCONFIG FROM FILEMAKER###
		###DO THE FFMPEG###
		#init folder to do the work in
		kwargs.processDir = os.path.join(conf.magneticTape.new_ingest,kwargs.aNumber)
		#make the full ffstr using the paths we have
		ffproc = ff.audio_init_ffproc(conf.magneticTape.cnxn,**kwargs)
		full_ffstr = ff.prefix(os.path.join(conf.magneticTape.new_ingest,kwargs.rawcapNumber) + "." + conf.ffmpeg.acodec_master_format) + ffproc.ff_suffix
		print full_ffstr
		#run ffmpeg on the file and make sure it completes successfully
		ffWorked = ffprocess(full_ffstr,kwargs.processDir)
		if not ffWorked:
			sys.exit()
		#special add for mono files
		if not "Stereo" in kwargs.channelConfig:
			ffWorked = mono_silence(kwargs)
		#if we need to reverse do it
		if ffproc.revface:
			print "reverse"
			#reverse(rawfname,face,aNumber,channelConfig,processDir)
		#if we need to normalize our sample rate to 96kHz, because we sped up or slowed down a recording, do it here
		if ffproc.hlvface or ffproc.dblface:
			print "sample rate normalize"
			#sampleratenormalize(processDir)
		###END THE FFMPEG###
		###EMBED BEXT###
		makebext(kwargs.aNumber,kwargs.processDir)
		#hashmove them to the repo dir
		#move(rawfname,aNumber,captureDir,archRepoDir)
		###END BEXT###
				
def main():
	###INIT VARS###
	global conf
	conf = rawconfig.config()
	parser = argparse.ArgumentParser(description="processes magnetic tape transfers")
	parser.add_argument('-m',dest='m',choices=['batch','single'],default=False,help='mode, for processing a single transfer or a batch in new_ingest')
	parser.add_argument('-i','--input',dest='i',help="the rawcapture file.wav to process, single mode only")
	args = parser.parse_args()
	###END INIT###

	###SINGLE MODE###
	if args.m == 'single':
		print "here"
		###INIT###
		file = args.i
		rawfname,ext = os.path.splitext(file)
		###END INIT###
		###GET ANUMBER FACE AND CHANNELCONFIG FROM FILEMAKER###
		#output = subprocess.check_output(["python","fm-stuff.py","-pi","-t","-p","nameFormat","-i",rawfname]) #get aNumber, channelconfig, face from FileMaker
		kwargs = {"rawcapNumber":args.i}
		process(kwargs)
	###END SINGLE MODE###
	###BATCH MODE###
	elif args.m is 'batch':
		for dirs,subdirs,files in os.walk(conf.magneticTape.captureDir):
			for file in files:
				###GET RID OF BS###
				if file.endswith(".gpk") or file.endswith(".mrk") or file.endswith(".bak") or file.endswith(".pkf"):
					try:
						os.remove(file)
					except:
						pass
				###END BS###
				###PROCESS CAPTURE###
				elif file.endswith(".wav"):
					try: #control for files currently in use
						subprocess.call("ffprobe " + os.path.join(dirs,file))
					except:
						continue
					###INIT###
					print file
					processNone = 0
					rawfname,ext = os.path.splitext(file)
					###END INIT###
					###GET ANUMBER FACE AND CHANNELCONFIG FROM FILEMAKER###
					kwargs = {"rawcapNumber":rawfname}
					process(kwargs)
				###END PROCESS CAPTURE###			
	###END BATCH MODE###						
if __name__ == '__main__':
	main()
