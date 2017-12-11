#!/usr/bin/env python
'''
make a Dissemination Information Package (DIP)
takes input for full path or canonical name + transaction number from Aeon
returns zipped folder on local /Desktop
'''
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
import getpass
###UCSB modules###
import config as rawconfig
import util as ut
import logger as log
import mtd
import makestartobject as makeso

def makeTranscodeList(args,archiveDir):
	'''
	returns list of objects which need to be transcoded to our access format
	'''
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
		for obj in args.i:
			startObj = subprocess.check_output([conf.python,os.path.join(conf.scriptRepo,"makestartobject.py"),"-i",obj])
			startObj = startObj.replace("\n","").replace("\r","")
			if startObj.endswith(".wav"):
				###MAKE LIST OF DIRS TO SEARCH FOR OBJECTS###
				endDirThousand = obj.replace("a","") #input arg here is a1234 but we want just the number
				if len(endDirThousand) < 5:#separates out the first digit and assigns an appropriate number of zeroes to match our dir structure
					endDirThousand = endDirThousand[:1] + "000"
				else:
					endDirThousand = endDirThousand[:2] + "000"
				startDir = os.path.join(archiveDir,endDirThousand,obj) #booshh
				startDirs.append(startDir)
				###END MAKE LIST###
			else:
				startDir = startObj
				startDirs.append(startDir)
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
		for obj in args.i:
			startDir = os.path.join(archiveDir,obj)
			startDirs.append(startDir)
			with ut.cd(startDir):
				for file in os.listdir(os.getcwd()):
					if file.endswith("b.wav"):
						b.append(os.path.join(os.getcwd(),file))
					elif file.endswith("a.wav") or file.endswith("m.wav"):
						a.append(os.path.join(os.getcwd(),file))
					elif file.endswith(".wav"):
						u.append(os.path.join(os.getcwd(),file))
					elif file.endswith(".mp3"):
						m.append(os.path.join(os.getcwd(),file))
					elif file.endswith(".tif"):
						i.append(os.path.join(os.getcwd(),file))
		###DEDUPE LISTS###
		print u
		print m
		print b
		print a
		if len(a) == 1 and len(u) == 1:
			if a[0].replace("m.wav",".wav") == u[0]:
				b.append(u[0])
				u.remove(u[0])
		for f in m: #loop thru mp3s to delete from other lists so we don't duplicate our efforts
			#assetName = re.search(obj,f) #grab just the canonical name part
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
		for f in u:
			for v in a:
				a.remove(v)
		for f in b: #loop thru broadcast master list and delete from other lists (transcoding from broadcast preferred)
			print obj
			assetName = obj #grab just the cusb-a1234 part
			for v in u:
				if assetName in v:
					u.remove(v)
			for v in a:
				if assetName in v:
					a.remove(v)
		###END DEDUPE###
	###END FOR DISCS###
	return a,b,u,m,i,startDirs

def make_transcodes(a,b,u,m,i,startDirs):
	#transcode where necessary
	for f in a:
		if args.t is True and args.hq is True:
			subprocess.call([conf.python,os.path.join(conf.scriptRepo,'makebroadcast.py'),'-i',f,'-t'])
		elif args.t is True:
			subprocess.call([conf.python,os.path.join(conf.scriptRepo,'makebroadcast.py'),'-i',f,'-t','-n','-mp3'])
		elif args.d is True and args.hq is True:
			subprocess.call([conf.python,os.path.join(conf.scriptRepo,'makebroadcast.py'),'-i',f,'-d','-sys',args.sys])
		elif args.d is True:
			subprocess.call([conf.python,os.path.join(conf.scriptRepo,'makebroadcast.py'),'-i',f,'-d','-n','-mp3','-sys',args.sys])
	for f in b:
		if args.t is True:
			subprocess.call([conf.python,os.path.join(conf.scriptRepo,'makemp3.py'),'-i',f])
		if args.d is True:
			subprocess.call([conf.python,os.path.join(conf.scriptRepo,'makemp3.py'),'-i',f])
	for f in u:
		if args.t is True and args.hq is True:
			subprocess.call([conf.python,os.path.join(conf.scriptRepo,'makebroadcast.py'),'-i',f,'-t'])
		elif args.t is True:
			subprocess.call([conf.python,os.path.join(conf.scriptRepo,'makebroadcast.py'),'-i',f,'-t','-n','-mp3'])
		elif args.d is True and args.hq is True:
			subprocess.call([conf.python,os.path.join(conf.scriptRepo,'makebroadcast.py'),'-i',f,'-d','-sys',args.sys])
		elif args.d is True:
			subprocess.call([conf.python,os.path.join(conf.scriptRepo,'makebroadcast.py'),'-i',f,'-d','-n','-mp3','-sys',args.sys])

def main():
	'''
	DO THE THING
	'''
	###INIT VARS###
	global conf
	conf = rawconfig.config()
	parser = argparse.ArgumentParser()
	parser.add_argument('-t','--tape',action='store_true',dest='t',default=False,help="make dip with audio template")
	parser.add_argument('-d','--disc',action='store_true',dest='d',default=False,help="make a dip with disc template")
	parser.add_argument('-i','--startObj',dest='i',nargs='+',required=True,help="the asset(s) that we want to make a dip for")
	parser.add_argument('-tn','--transactionNumber',dest='tn',required=True,help="the transaction number from aeon")
	parser.add_argument('-sys','--systemNumber',dest='sys',help="the system number for a disc in our catalog (Alma MMS ID)")
	parser.add_argument('-hq','--highquality',action='store_true',dest='hq',default=False,help="don't transcode to mp3, dip a cd-quality wave")
	parser.add_argument('-z','--zip',action='store_true',dest='z',default=False,help="compress the dip folder when everything is in there")
	global args
	args = parser.parse_args()
	#log.log("started")
	if args.t is True:
		archiveDir = conf.magneticTape.repo #grab archive directory for audio tapes
	elif args.d is True:
		#archiveDir = config.get("discs","repo")
		startObj = subprocess.check_output([conf.python,os.path.join(conf.scriptRepo,"makestartobject.py"),"-i",args.i])
		if "None" in startObj:
			print "Sorry, it looks like this hasn't been digitized."
			print "Double check the item name"
			sys.exit()
		startObj = startObj.replace("\\","/")[:-2]
		print startObj
		archiveDir = os.path.dirname(os.path.dirname(startObj))
	else:
		print "Buddy, you gotta specify if this is a tape or a disc"
		sys.exit()
	###END INIT###
	#log.log("end init")

	###GENERATE TRANSCODE LISTS###
	a,b,u,m,i,startDirs = makeTranscodeList(args, archiveDir) #make a dictionary of files to work with
	###do the transcodes
	make_transcodes(a,b,u,m,i,startDirs)

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
	print veggies

	#hashmove to dir on desktop named for TN
	try:
		dipDir = os.path.join(os.environ["HOME"], "Desktop",args.tn)
	except:
		dipDir = os.path.join(os.environ["USERPROFILE"], "Desktop",args.tn)
	if not os.path.isdir(dipDir):
		os.makedirs(dipDir)
	for f in veggies:
		subprocess.call([conf.python,os.path.join(conf.scriptRepo,'hashmove.py'),'-c',f,dipDir])

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
if __name__ == '__main__':
	main()
