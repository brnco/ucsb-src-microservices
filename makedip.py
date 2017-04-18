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
import ConfigParser
import getpass

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
			with cd(startDir):
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
			for v in u:
				if assetName.group() in v:
					u.remove(v)
			for v in a:
				if assetName.group() in v:
					a.remove(v)
		###END DEDUPE###
	###END FOR TAPES###
	###FOR DISCS###
	elif args.d is True:
		for obj in args.so:
			startDir = os.path.join(archiveDir,obj)
			startDirs.append(startDir)
			with cd(startDir):
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
		for obj in args.so:
			for f in m: #loop thru mp3s to delete from other lists so we don't duplicate our efforts
				_assetName = re.search(obj,f) #grab just the canonical name part
				assetName = obj
				foo = raw_input("eh")
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
	parser = argparse.ArgumentParser()
	parser.add_argument('-t','--tape',action='store_true',dest='t',default=False,help="make dip with audio template")
	parser.add_argument('--disc',action='store_true',dest='d',default=False,help="make a dip with disc template")
	parser.add_argument('-so','--startObj',dest='so',nargs='+',required=True,help="the asset(s) that we want to make a dip for")
	parser.add_argument('-tn','--transactionNumber',dest='tn',required=True,help="the transaction number from aeon")	
	#parser.add_argument('-hq','--highquality',action='store_true',dest='hq',default=False,help="don't transcode to mp3, dip a cd-quality wave")
	#parser.add_argument('-a','--archival',dest='a',help="don't transcode a broadcast master or mp3, dip the archival master")
	parser.add_argument('-z','--zip',action='store_true',dest='z',default=False,help="compress the dip folder when everything is in there")
	parser.add_argument('-mb','--makeBroadcast',nargs='+',choices=['ff','s','mp3','n','d'],dest='mb',help="options for makebroadcast")
	args = parser.parse_args()
	config = ConfigParser.ConfigParser()
	dn, fn = os.path.split(os.path.abspath(__file__)) #grip the path to the directory where ~this~ script is located
	config.read(os.path.join(dn,"microservices-config.ini"))
	mmrepo = config.get('global','scriptRepo')
	if args.t is True:
		archiveDir = config.get("magneticTape","repo") #grab archive directory for audio tapes
	elif args.d is True:
		archiveDir = config.get("discs","repo")
	else:
		print "Buddy, you gotta specify if this is a tape or a disc"
		sys.exit()
	###END INIT###

	###GENERATE TRANSCODE LISTS###
	a,b,u,m,i,startDirs = makeTranscodeList(args, archiveDir) #make a dictionary of files to work with
	#transcode where necessary
	for f in a:
		if args.t is True:
			subprocess.call(['python',os.path.join(mmrepo,'makebroadcast.py'),'-so',f,'-t'])
	#for f in b:
		#if args.t is True:
			#subprocess.call(['python',os.path.join(mmrepo,'makebroadcast.py'),'-so',f,'-t'])
	for f in u:
		if args.t is True:
			subprocess.call(['python',os.path.join(mmrepo,'makebroadcast.py'),'-so',f,'-t'])
	
	#make a final list of stuff we gonna dip
	veggies = []
	for dir in startDirs:
		for file in os.listdir(dir):
			if file.endswith(".mp3") and file not in m:
				veggies.append(os.path.join(dir,file))
			if file.endswith(".tif"):
				veggies.append(os.path.join(dir,file))
			if file.endswith("b.wav"):
				veggies.append(os.path.join(dir,file))
	
	#hashmove to dir on desktop named for TN
	dipDir = os.path.join("C:/Users",getpass.getuser(),"Desktop",args.tn)
	if not os.path.isdir(dipDir):
		os.makedirs(dipDir)
	for f in veggies:
		subprocess.call(['python',os.path.join(mmrepo,'hashmove.py'),'-c',f,dipDir])
	
	#compress dir on desktop
	if args.z is True:
		tnDir = os.path.join("C:/Users/",getpass.getuser(),"Desktop",args.tn)
		with cd(tnDir):
			zf = zipfile.ZipFile(tnDir + ".zip","w")
			for f in os.listdir(os.getcwd()):
				zf.write(os.path.basename(os.path.join(dipDir,f)),compress_type=zipfile.ZIP_DEFLATED)
			zf.close()

dependencies()
main()