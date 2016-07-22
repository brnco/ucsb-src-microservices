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

def deletebs(captureDir):
	for dirs,subdirs,files in os.walk(captureDir):
		for f in files:
			if f.endswith(".gpk") or f.endswith(".mrk") or f.endswith(".bak"):
				os.remove(os.path.join(captureDir,f))
	return
		
#make list of files to process
def makelist(captureDir,toProcessDir,flist = {}):
	for dirs, subdirs, files in os.walk(toProcessDir):
		for f in files:
			aNum,ext = os.path.splitext(f) #grab aNum
			with open(os.path.join(dirs,f)) as arb:
				fulline = csv.reader(arb, delimiter=",") #use csv lib to read it line by line
				for x in fulline: #result is list
					flist[aNum] = x #makes dict of aNumber : [rawfname,track configuration] values
	return flist

#do the ffmpeg stuff to each file	
def ffprocess(aNumber,process,captureDir,mmrepo):
	rawfname = process[0]
	try:
		channelConfig = process[1]
	except IndexError:
		channelConfig = "nothing"
	try:
		reverseA = process[2]
	except IndexError:
		reverseA = "nothing"
	try:
		reverseB = process[3]
	except IndexError:
		reverseB = "nothing"
	dirNumber = aNumber	
	if aNumber.endswith("A") or aNumber.endswith("B"):
		dirNumber = aNumber[:-1]
	processingDir = os.path.join(captureDir,dirNumber)
	endObj1 = os.path.join(processingDir,"cusb-" + aNumber + "a.wav") #name of archival master when we're done
	endObj2 = os.path.join(processingDir,"cusb-" + aNumber + "e.wav")

	#make a processing directory named after first attr in fm export: aNumber
	if not os.path.exists(processingDir):
		os.makedirs(processingDir)
	remove silence from raw transfer if audio quieter than -50dB, longer than 10s of silence
	if not os.path.exists(endObj1):
		subprocess.call('ffmpeg -i ' + os.path.join(captureDir,rawfname) + '.wav -af silenceremove=0:0:-50dB:-10:1:-50dB -acodec pcm_s24le ' + endObj1) 
	#let's make sure the channels are right
	with cd(processingDir):
		#the following call pipes the ffprobe stream output back to this script
		ffdata = subprocess.Popen(["ffprobe","-show_streams","-of","flat",endObj1],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		data, err = ffdata.communicate() #separate it so it's useful
		if "stereo" in data: #ok so all of our raw captures are stereo so this ~should~ always trigger
			if channelConfig == '1/4-inch Half Track Mono':
				subprocess.call(["python",os.path.join(mmrepo,"changechannels.py"),"-so",endObj1]) #call change channels to split streams to separate files, renaming them correctly
				if deleteA == '1':
					os.remove("cusb-" + aNumber "Aa.wav")
				if deleteB == '1':
					os.remove("cusb-" + aNumber "Ba.wav")
				try:
					if reverseA == '1':
						subprocess.call("ffmpeg -i cusb-" + aNumber + "Aa.wav -c:a copy -af areverse " + endObj2)
						os.remove(endObj1)
						os.rename(endObj2, endObj1)
					if reverseB == '1':
						subprocess.call("ffmpeg -i cusb-" + aNumber + "Ba.wav -c:a copy -af areverse " + endObj2)
						os.remove(endObj1)
						os.rename(endObj2, endObj1)
				except:
					pass
			if channelConfig == '1/4-inch Full Track Mono': #we can really only downmix to mono for speech, it's not preservation best practice for music
				subprocess.call(["ffmpeg","-i",endObj1,"-ac","1",endObj2]) #downmix to mono
				os.remove(endObj1) #can't overwrite with ffmpeg it's trash
				os.rename(endObj2,endObj1)
	return

#do the fancy library thing to each file	
def bextprocess(aNumber,process,bextsDir,captureDir):
	dirNumber = aNumber
	if aNumber.endswith("A") or aNumber.endswith("B"):
		dirNumber = aNumber[:-1]
	processingDir = os.path.join(captureDir,dirNumber)
	endObj1 = os.path.join(processingDir,"cusb-" + aNumber + "a.wav")
	endObj1A = os.path.join(processingDir,"cusb-" + aNumber + "Aa.wav")
	endObj1B = os.path.join(processingDir,"cusb-" + aNumber + "Ba.wav")
	#clear mtd already in there
	
	#embed checksums
	print "hashing data chunk of " + aNumber
	if os.path.exists(endObj1):
		subprocess.call('bwfmetaedit --in-core-remove ' + endObj1)
		subprocess.call('bwfmetaedit --MD5-Embed-Overwrite ' + endObj1)
	if os.path.exists(endObj1A):
		subprocess.call('bwfmetaedit --in-core-remove ' + endObj1A)
		subprocess.call('bwfmetaedit --MD5-Embed-Overwrite ' + endObj1A)
	if os.path.exists(endObj1B):
		subprocess.call('bwfmetaedit --in-core-remove ' + endObj1B)
		subprocess.call('bwfmetaedit --MD5-Embed-Overwrite ' + endObj1B)
	
	#embed bext metadata based on FM output
	bextFile = os.path.join(bextsDir,'cusb-' + aNumber + '-bext.txt')
	if os.path.exists(bextFile):
		print "embedding bext in " + aNumber
		with open(bextFile) as bf:
			bextlst = bf.readlines()
			bextstr = str(bextlst)
			bextstr = bextstr.strip("['']")
			#bextstr = bextstr.replace('"','')
			foo = 'bwfmetaedit ' + bextstr + ' ' + endObj1
			if os.path.exists(endObj1):
				subprocess.call('bwfmetaedit ' + bextstr + ' ' + endObj1)
			elif os.path.exists(endObj1A):
				subprocess.call('bwfmetaedit ' + bextstr + ' ' + endObj1A)
			elif os.path.exists(endObj1B):
				subprocess.call('bwfmetaedit ' + bextstr + ' ' + endObj1B)
			#print foo
	return

#hashmove processing folder to the repo	
def move(f,opts,captureDir,mmrepo,archRepoDir):
	aNumber = "a" + str(opts[0])
	if aNumber.endswith("A") or aNumber.endswith("B"):
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
		output = subprocess.Popen(['python',os.path.join(mmrepo,'hashmove.py'),processingDir,endDir],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		foo,err = output.communicate()
		sourcehash = re.search('srce\s\S+\s\w{32}',foo)
		desthash = re.search('dest\s\S+\s\w{32}',foo)
		dh = desthash.group()
		sh = sourcehash.group()
		bexttxt = os.path.join("R:/audio/avlab/fm-exports/bexttxts","cusb-" + dirNumber + "-bext.txt")
		startObj1 = os.path.join("R:/audio/avlab/fm-exports/to_process",f + ".txt")
		if sh[-32:] == dh[-32:]:
			os.remove(os.path.join(captureDir,f + ".wav"))
			if os.path.exists(bexttxt): #can't give os.remove a file object it's gotta be a string grrrrr
				os.remove(os.path.join("R:/audio/avlab/fm-exports/bexttxts","cusb-" + dirNumber + "-bext.txt"))
			if os.path.exists(startObj1):
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
	#htm-update test
	#get rid of the crap
	#deletebs(captureDir)
	
	#make a list of files to work on
	flist = makelist(captureDir,toProcessDir)
	
	for aNumber, process in flist.iteritems():

		#run the ffmpeg stuff we gotta do (silence removal, to add: changechannels and splitfiles)
		#try:
			ffprocess(aNumber,process,captureDir,mmrepo)
			foo = raw_input("eh")
		#except:
			#pass
		
		#try:
			#pop the bext info into each file
			#bextprocess(f,opts,bextsDir,captureDir)
		#except:
			#pass
		
		#try:
			#hashmove them to the repo dir
			#move(f,opts,captureDir,mmrepo,archRepoDir)
		#except:
			#pass
	return

dependencies()
main()