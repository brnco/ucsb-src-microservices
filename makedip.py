#!/usr/bin/env python
#makedip
#coding=UTF-8


import os
import subprocess
import sys
import glob
import re
import argparse
import shutil
import zipfile
import zlib
import time
from distutils import spawn
import imp
import getpass

def dependencies():
	depends = ['ffmpeg','ffprobe']
	for d in depends:
		if spawn.find_executable(d) is None:
			print "Buddy, you gotta install " + d
			sys.exit()
	return

def makeTranscodeList(args,archiveDir):
	###INIT VARS###
	a = [] #archive masters
	b = [] #broadcast masters
	m = [] #mp3s
	u = [] #unknowns (known)
	i = [] #images
	startDirs = []
	###END INIT###
	###FOR TAPES###
	if args.t is True:
		for obj in args.so:
			startObj = subprocess.check_output(["python","makestartobject.py","-so",obj])
			###MAKE LIST OF DIRS TO SEARCH FOR OBJECTS###
			endDirThousand = obj.replace("a","") #input arg here is a1234 but we want just the number
			if len(endDirThousand) < 5:#separates out the first digit and assigns an appropriate number of zeroes to match our dir structure
				endDirThousand = endDirThousand[:1] + "000"
			else:
				endDirThousand = endDirThousand[:2] + "000"
			startDir = os.path.join(archiveDir,endDirThousand,obj) #booshh
			startDirs.append(startDir)
			###END MAKE LIST###
			###FIND OBJECTS###
			with ut.cd(startDir):
				for file in os.listdir(os.getcwd()):
					if file.endswith("b.wav"):
						b.append(os.path.join(os.getcwd(),file))
					elif file.endswith("a.wav"):
						a.append(os.path.join(os.getcwd(),file))
					elif file.endswith(".wav"):
						u.append(os.path.join(os.getcwd(),file))
					elif file.endswith(".mp3"):
						m.append(os.path.join(os.getcwd(),file))
		###DEDUPE LISTS###
		###we want to know if there are mp3s already for these objects or which file to transcode
		for f in m:
			assetName = re.search('cusb-a\d+',f) #grab just the cusb-a1234 part
			for v in u: #loop thru found mp3s in dir
				if assetName.group() in v: #if the string cubs-a1234 is in the list of mp3s
					u.remove(v)
			for v in b:
				if assetName.group() in v:
					b.remove(v)
			for v in a:
				if assetName.group() in v:
					a.remove(v)
		for f in b:
			assetName = re.search('cusb-a\d+',f)
			raw_assetName = re.search('\w{8}-\w{4}-\w{4}-\w{4}-',f)
			for v in u:
				if assetName.group() in v or raw_assetName.group() in v:
					u.remove(v)
			for v in a:
				if assetName.group() in v or raw_assetName.group() in v:
					a.remove(v)
		###END DEDUPE###
	###END FOR TAPES###
	###FOR DISCS###
	elif args.d is True:
		for obj in args.so:
			startDir = os.path.join(archiveDir,obj)
			startDirs.append(startDir)
			with ut.cd(startDir):
				for file in os.listdir(os.getcwd()):
					if file.endswith("b.wav"):
						b.append(os.path.join(os.getcwd(),file))
					elif file.endswith("a.wav"):
						a.append(os.path.join(os.getcwd(),file))
					elif file.endswith(".wav"):
						u.append(os.path.join(os.getcwd(),file))
					elif file.endswith(".mp3"):
						m.append(os.path.join(os.getcwd(),file))
					elif file.endswith(".tif"):
						i.append(os.path.join(os.getcwd(),file))
		###DEDUPE LISTS###
		for f in m: #loop thru mp3s to delete from other lists so we don't duplicate our efforts
			#_assetName = re.search(obj,f) #grab just the canonical name part
			assetName = obj
			for v in u: #loop thru found mp3s in dir
				if assetName in v: #if the string cubs-a1234 is in the list of mp3s
					u.remove(v)
			for v in b:
				if assetName in v:
					b.remove(v)
			for v in a:
				if assetName in v:
					a.remove(v)
		for f in b: #loop thru broadcast master list and delete from other lists (transcoding from broadcast preferred)
			#assetName = re.search('cusb-a\d+',f) #grab just the cusb-a1234 part
			for v in u:
				if assetName in v:
					u.remove(v)
			for v in a:
				if assetName in v:
					a.remove(v)
		###END DEDUPE###
	###END FOR DISCS###
	return a,b,u,m,i,startDirs
	
def main():
	###INIT VARS###
	dn, fn = os.path.split(os.path.abspath(__file__))
	global log
	log = imp.load_source('log',os.path.join(dn,'logger.py'))
	global conf
	rawconfig = imp.load_source('config',os.path.join(dn,'config.py'))
	conf = rawconfig.config()
	global ut
	ut = imp.load_source("util",os.path.join(dn,"util.py"))
	parser = argparse.ArgumentParser()
	parser.add_argument('-t','--tape',action='store_true',dest='t',default=False,help="make dip with audio template")
	parser.add_argument('-d','--disc',action='store_true',dest='d',default=False,help="make a dip with disc template")
	parser.add_argument('-so','--startObj',dest='so',nargs='+',required=True,help="the asset(s) that we want to make a dip for")
	parser.add_argument('-tn','--transactionNumber',dest='tn',required=True,help="the transaction number from aeon")	
	parser.add_argument('-hq','--highquality',action='store_true',dest='hq',default=False,help="don't transcode to mp3, dip a cd-quality wave")
	parser.add_argument('-z','--zip',action='store_true',dest='z',default=False,help="compress the dip folder when everything is in there")
	args = parser.parse_args()
	log.log("started")
	if args.t is True:
		archiveDir = conf.magneticTape.repo #grab archive directory for audio tapes
	elif args.d is True:
		#archiveDir = config.get("discs","repo")
		startObj = subprocess.check_output(["python",os.path.join(conf.scriptRepo,"makestartobject.py"),"-so",args.so])
		startObj = startObj.replace("\\","/")[:-2]
		print startObj
		archiveDir = os.path.dirname(os.path.dirname(startObj))
	else:
		print "Buddy, you gotta specify if this is a tape or a disc"
		sys.exit()
	###END INIT###

	###GENERATE TRANSCODE LISTS###
	a,b,u,m,i,startDirs = makeTranscodeList(args, archiveDir) #make a dictionary of files to work with
	#transcode where necessary
	for f in a:
		if args.t is True and args.hq is True:
			subprocess.call(['python',os.path.join(conf.scriptRepo,'makebroadcast.py'),'-so',f,'-t'])
		elif args.t is True:
			subprocess.call(['python',os.path.join(conf.scriptRepo,'makebroadcast.py'),'-so',f,'-t','-n','-mp3'])
	for f in b:
		if args.t is True:
			subprocess.call(['python',os.path.join(conf.scriptRepo,'makemp3.py'),'-so',f])
	for f in u:
		if args.t is True and args.hq is True: 
			subprocess.call(['python',os.path.join(conf.scriptRepo,'makebroadcast.py'),'-so',f,'-t'])
		elif args.t is True:
			subprocess.call(['python',os.path.join(conf.scriptRepo,'makebroadcast.py'),'-so',f,'-t','-n','-mp3'])
	
	#make a final list of stuff we gonna dip
	veggies = []
	for dir in startDirs:
		for file in os.listdir(dir):
			if args.hq is False:
				if file.endswith(".mp3") and file not in m:
					veggies.append(os.path.join(dir,file))
			elif args.hq is True:
				if file.endswith("b.wav"):
					veggies.append(os.path.join(dir,file))
			if file.endswith(".tif"):
				veggies.append(os.path.join(dir,file))
			
	
	#hashmove to dir on desktop named for TN
	try:	
		dipDir = os.path.join(os.environ["HOME"], "Desktop",args.tn)
	except:
		dipDir = os.path.join(os.environ["USERPROFILE"], "Desktop",args.tn)
	if not os.path.isdir(dipDir):
		os.makedirs(dipDir)
	for f in veggies:
		subprocess.call(['python',os.path.join(conf.scriptRepo,'hashmove.py'),'-c',f,dipDir])
	
	#compress dir on desktop
	if args.z is True:
		tnDir = dipDir
		with ut.cd(tnDir):
			zf = zipfile.ZipFile(tnDir + ".zip","w")
			for f in os.listdir(os.getcwd()):
				zf.write(os.path.basename(os.path.join(dipDir,f)),compress_type=zipfile.ZIP_DEFLATED)
			zf.close()
		if os.path.exists(tnDir + ".zip"):
			shutil.rmtree(tnDir)

dependencies()
main()