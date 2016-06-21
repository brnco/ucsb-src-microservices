#avlab-magneticTape

import ConfigParser
import getpass
import os
import subprocess
import csv
import re
from distutils import spawn

#check that we have the required software to run this script
def dependencies():
	depends = ['bwfmetaedit','ffmpeg','ffprobe']
	for d in depends:
		if spawn.find_executable(d) is None:
			print "Buddy, you gotta install " + d
			sys.exit()
	return

#Context manager for changing the current working directory
class cd:
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

#make list of files to process
def makelist(captureDir,toProcessDir,flist = {}):
	for dirs, subdirs, files in os.walk(captureDir):
		for f in files:
			rawfname,ext = os.path.splitext(f) #grab raw file name from os.walk
			txtinfo = os.path.join(toProcessDir,rawfname + '.txt') #init var for txt file that tells us how to process
			if os.path.exists(txtinfo): #if said text file exists
				with open(txtinfo) as arb:
					fulline = csv.reader(arb, delimiter=",") #use csv lib to read it line by line
					for x in fulline: #result is list
						flist[rawfname] = x #makes dict of rawfilename : [anumber(wihtout the 'a'),track configuration] values
	return flist

#do the ffmpeg stuff to each file	
def ffprocess(flist,captureDir,mmrepo):
	for f in flist:
		opts = flist[f]
		aNumber = "a" + str(opts[0])
		dirNumber = aNumber
		if aNumber.endswith("A") or aNumber.endswith("B"):
			dirNumber = aNumber[:-1]
		try:
			channelConfig = str(opts[1])
		except IndexError:
			channelConfig = "nothing"
		processingDir = os.path.join(captureDir,dirNumber)
		endObj1 = os.path.join(processingDir,"cusb-" + aNumber + "a.wav") #name of archival master when we're done
		endObj2 = os.path.join(processingDir,"cusb-" + aNumber + "e.wav")
		#make a processing directory named after first attr in fm export: aNumber
		if not os.path.exists(processingDir):
			os.makedirs(processingDir)
			#remove silence from raw transfer if audio quieter than -50dB, longer than 10s of silence
		if not os.path.exists(endObj1):
			subprocess.call('ffmpeg -i ' + os.path.join(captureDir,f) + '.wav -af silenceremove=0:0:-50dB:-10:1:-50dB -acodec pcm_s24le ' + endObj1) 
		
		#let's make sure the channels are right
		with cd(processingDir):
			#the following call pipes the ffprobe stream output back to this script
			ffdata = subprocess.Popen(["ffprobe","-show_streams","-of","flat",endObj1],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
			data, err = ffdata.communicate() #separate it so it's useful
			print channelConfig
			if "stereo" in data: #ok so all of our raw captures are stereo so this ~should~ always trigger
				if channelConfig == '1/4-inch Half Track Mono':
					subprocess.call(["python",os.path.join(mmrepo,"changechannels.py"),"-so",endObj1]) #call change channels to split streams to separate files, renaming them correctly
				if channelConfig == '1/4-inch Full Track Mono':
					subprocess.call(["ffmpeg","-i",endObj1,"-ac","1",endObj2]) #downmix to mono
					os.remove(endObj1) #can't overwrite with ffmpeg it's trash
					os.rename(endObj2,endObj1)
				
			#split files larger than 2GB	
			#statinfo = os.stat(endObj1)
			#eo1size = statinfo.st_size
			#if eo1size >= 2147483648:
				#print "too big too wide"
	return

#do the fancy library thing to each file	
def bextprocess(flist,bextsDir,captureDir):
	for f in flist:
		opts = flist[f]
		aNumber = "a" + str(opts[0])
		print "embedding bext in " + aNumber
		dirNumber = aNumber
		if aNumber.endswith("A") or aNumber.endswith("B"):
			dirNumber = aNumber[:-1]
		processingDir = os.path.join(captureDir,dirNumber)
		endObj1 = os.path.join(processingDir,"cusb-" + aNumber + "a.wav")
		#clear mtd already in there
		subprocess.call('bwfmetaedit --in-core-remove ' + endObj1)
		#embed checksums
		subprocess.call('bwfmetaedit --MD5-Embed-Overwrite ' + endObj1)
		#embed bext metadata based on FM output
		bextFile = os.path.join(bextsDir,'cusb-' + aNumber + '-bext.txt')
		if os.path.exists(bextFile):
			with open(bextFile) as bf:
				bextlst = bf.readlines()
				bextstr = str(bextlst)
				bextstr = bextstr.strip("['']")
				bextstr = bextstr.replace('"','')
				subprocess.call('bwfmetaedit ' + bextstr + ' ' + endObj1)
		foo = raw_input("eh")
	return

#hashmove each file to the repo	
def move(flist,captureDir,mmrepo,archRepoDir):
	for f in flist:
		opts = flist[f]
		aNumber = "a" + str(opts[0])
		dirNumber = aNumber
		if aNumber.endswith("A") or aNumber.endswith("B"):
			dirNumber = aNumber[:-1]
		processingDir = os.path.join(captureDir,dirNumber)
		endDirThousand = aNumber.replace("a","") #input arg here is a1234 but we want just the number
		#the following separates out the first digit and assigns an appropriate number of zeroes to match our dir structure
		if len(endDirThousand) < 5:
			endDirThousand = endDirThousand[:1] + "000"
		else:
			endDirThousand = endDirThousand[:2] + "000"
		endDir = os.path.join(archRepoDir,endDirThousand,dirNumber)
		#hashmove it and grip the output so we can delete the raw files YEAHHH BOY
		output = subprocess.Popen(['python',os.path.join(mmrepo,'hashmove.py'),processingDir,endDir],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		foo,err = output.communicate()
		sourcehash = re.search('srce\s\S+\s\w{32}',foo)
		desthash = re.search('dest\s\S+\s\w{32}',foo)
		dh = desthash.group()
		sh = sourcehash.group()
		if sh[-32:] == dh[-32:]:
			os.remove(os.path.join(captureDir,f + ".wav"))
			os.remove(os.path.join("R:/audio/avlab/fm-exports/bexttxts","cusb-" + dirNumber + "-bext.txt"))
			os.remove(os.path.join("R:/audio/avlab/fm-exports/to_process",f + ".txt"))
	
	return

def main():
	#initialize the stuff
	config = ConfigParser.ConfigParser()
	config.read("C:/Users/" + getpass.getuser() + "/microservices-config.ini")
	captureDir = config.get('magneticTape','magTapeCaptureDir')
	archRepoDir = config.get('magneticTape','magTapeArchDir')
	toProcessDir = config.get('magneticTape','magTapeToProcessDir')
	bextsDir = config.get('magneticTape','magTapebexts')
	logDir = config.get('magneticTape','magTapeLogs')
	mmrepo = config.get('global','scriptRepo')

	#make a list of files to work on
	flist = makelist(captureDir,toProcessDir)

	#run the ffmpeg stuff we gotta do (silence removal, to add: changechannels and splitfiles)
	ffprocess(flist,captureDir,mmrepo)
	
	#pop the bext info into each file
	bextprocess(flist,bextsDir,captureDir)

	#hashmove them to the repo dir
	move(flist,captureDir,mmrepo,archRepoDir)
	
	return

dependencies()
main()