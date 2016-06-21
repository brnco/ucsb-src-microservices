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

def makeTranscodeList(startObjs,archiveDir,mediatype):
	a = [] #archive masters
	b = [] #broadcast masters
	m = [] #mp3s
	u = [] #unknowns (known)
	i = [] #images
	startDirs = []
	if mediatype == 'istape':
		for obj in startObjs:
			endDirThousand = obj.replace("a","") #input arg here is a1234 but we want just the number
			#the following separates out the first digit and assigns an appropriate number of zeroes to match our dir structure
			if len(endDirThousand) < 5:
				endDirThousand = endDirThousand[:1] + "000"
			else:
				endDirThousand = endDirThousand[:2] + "000"
			startDir = os.path.join(archiveDir,endDirThousand,obj) #booshh
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
		#find
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
			assetName = re.search('cusb-a\d+',f) #grab just the cusb-a1234 part
			for v in u:
				if assetName.group() in v:
					u.remove(v)
			for v in a:
				if assetName.group() in v:
					a.remove(v)
	elif mediatype == 'isdisc':
		for obj in startObjs:
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
		#find
		for obj in startObjs:
			for f in m: #loop thru mp3s to delete from other lists so we don't duplicate our efforts
				assetName = re.search(obj,f) #grab just the canonical name part
				for v in u: #loop thru found mp3s in dir
					if assetName.group() in v: #if the string cubs-a1234 is in the list of mp3s
						u.remove(v)
				for v in b:
					if assetName.group() in v:
						b.remove(v)
				for v in a:
					if assetName.group() in v:
						a.remove(v)
			for f in b: #loop thru broadcast master list and delete from other lists (transcoding from broadcast preferred)
				assetName = re.search('cusb-a\d+',f) #grab just the cusb-a1234 part
				for v in u:
					if assetName.group() in v:
						u.remove(v)
				for v in a:
					if assetName.group() in v:
						a.remove(v)
	return a,b,u,m,i,startDirs
	
def main():
	#input args for resources to pull & TN
	parser = argparse.ArgumentParser()
	parser.add_argument('-t','--tape',action='store_true',dest='tape',default=False,help="make dip with audio template")
	parser.add_argument('-d','--disc',action='store_true',dest='disc',default=False,help="make a dip with disc template")
	parser.add_argument('-so','--startObj',dest='so',nargs='+',required=True,help="the asset that we want to make a dip for")
	parser.add_argument('-tn','--transactionNumber',dest='tn',required=True,help="the transaction number from aeon")	
	parser.add_argument('-hq','--highquality',dest='hq',help="don't transcode to mp3, dip a cd-quality wave")
	#parser.add_argument('-a','--archival',dest='a',help="don't transcode a broadcast master or mp3, dip the archival master")
	parser.add_argument('-comp','--compress',action='store_true',dest='compress',default=False,help="compress the dip folder when everything is in there")
	#parser.add_argument('-r','--rights',dest='r',default="©2016 The Regents of the University of California",help="a copyright statement for the asset")
	args = parser.parse_args()
	
	
	
	#initialize our parser for the config file so we can get paths later
	config = ConfigParser.ConfigParser()
	config.read("C:/Users/" + getpass.getuser() + "/microservices-config.ini")
	mmrepo = config.get('global','scriptRepo')
	#find resources
	if args.tape is True:
		istape = "istape"
		archiveDir = config.get("magneticTape","magTapeArchDir") #grab archive directory for audio tapes
		a,b,u,m,i,startDirs = makeTranscodeList(args.so, archiveDir, istape) #make a dictionary of files to work with
	
	if args.disc is True:
		isdisc = 'isdisc'
		archiveDir = config.get("discs","archRepoDir")
		a,b,u,m,i,startDirs = makeTranscodeList(args.so, archiveDir, isdisc) #make a dictionary of files to work with
	#transcode where necessary
	for f in a:
		subprocess.call(['python',os.path.join(mmrepo,'makebroadcast.py'),'-mp3',f,])
	for f in b:
		subprocess.call(['python',os.path.join(mmrepo,'makebroadcast.py'),'-mp3',f,])
	for f in u:
		subprocess.call(['python',os.path.join(mmrepo,'makebroadcast.py'),'-mp3',f,])
	
	#make a final list of stuff we gonna dip
	veggies = []
	for dir in startDirs:
		for file in os.listdir(dir):
			if file.endswith(".mp3") and file not in m:
				veggies.append(os.path.join(dir,file))
			if file.endswith(".tif"):
				veggies.append(os.path.join(dir,file))
	
	#hashmove to dir on desktop named for TN
	dipDir = os.path.join("C:/Users",getpass.getuser(),"Desktop",args.tn)
	if not os.path.isdir(dipDir):
		os.makedirs(dipDir)
	for f in veggies:
		subprocess.call(['python',os.path.join(mmrepo,'hashmove.py'),'-c',f,dipDir])
	
	#compress dir on desktop
	if args.compress is True:
		with cd("C:/Users/" + getpass.getuser() + "/Desktop"):
			zf = zipfile.ZipFile(args.tn + ".zip","w")
			for f in os.listdir(args.tn):
				zf.write(os.path.join(dipDir,f),compress_type=zipfile.ZIP_DEFLATED)
			zf.close()

dependencies()
main()