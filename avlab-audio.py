#!/usr/bin/env python
#avlab-magneticTape

import ConfigParser
import argparse
import getpass
import os
import subprocess
import csv
import re
import time
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
			if not f.endswith(".txt"): #SOMETIMES FILEMAKER DOESN'T EXPORT THE .TXT PART BECAUSE IT'S GREAT AND I LOVE IT
				f = f + ".txt"
			rawfname,ext = os.path.splitext(f) #grab raw file name from os.walk
			print rawfname
			txtinfo = os.path.join(toProcessDir,rawfname + '.txt') #init var for full path of txt file that tells us how to process
			if os.path.exists(txtinfo): #if said text file exists
				with open(txtinfo) as arb:
					fulline = csv.reader(arb, delimiter=",") #use csv lib to read it line by line
					for x in fulline: #result is list
						flist[rawfname] = x #makes dict of rawfilename : [anumber(wihtout the 'a'),track configuration] values
	return flist

#do the ffmpeg stuff to each file	
def ffprocess(aNumber,rawfname,process,captureDir,toProcessDir,mmrepo):
	processDir = os.path.join(captureDir,aNumber)
	output = subprocess.Popen(['python',os.path.join(mmrepo,'fm-ffhandler.py'),rawfname + ".txt"],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	ffmpegstring,err = output.communicate()
	print ffmpegstring
	ffmpeglist = ffmpegstring.split()
	returncode = 0
	revstr0 = ''
	revstr1 = ''
	revstr01 = ''
	match = ''
	
	if not os.path.exists(processDir):
		os.makedirs(processDir)
	time.time
	#do it
	with cd(processDir):
		try:
			output = subprocess.check_output(ffmpeglist,shell=True)
			returncode = 0
		except subprocess.CalledProcessError,e:
			output = e.output
			returncode = output
		if returncode == 0:
			#os.remove(os.path.join(captureDir,rawfname + ".wav"))
			print "foo"
		else:
			return
		returncode = 0	
		
		#reverse if necessary
		#input files are deleted by makereverse if the process was successful
		for x in process:
			if x == "rev_fAB":
				subprocess.call(['python',os.path.join(mmrepo,"makereverse.py"),os.path.join(processDir,rawfname + "-processed.wav")])
			if x == "rev_fCD":
				subprocess.call(['python',os.path.join(mmrepo,"makereverse.py"),os.path.join(processDir,rawfname + "-processed.wav")])
			if x == "rev_fA":
				subprocess.call(['python',os.path.join(mmrepo,"makereverse.py"),os.path.join(processDir,rawfname + "left.wav")])
			if x == "rev_fB":
				subprocess.call(['python',os.path.join(mmrepo,"makereverse.py"),os.path.join(processDir,rawfname + "right.wav")])
			if x == "rev_fC":
				subprocess.call(['python',os.path.join(mmrepo,"makereverse.py"),os.path.join(processDir,rawfname + "left.wav")])
			if x == "rev_fD":
				subprocess.call(['python',os.path.join(mmrepo,"makereverse.py"),os.path.join(processDir,rawfname + "right.wav")])
		
		#give comp time to catch up
		time.sleep(2)
		
		#ok so by now every file in the processing dir is the correct channel config & plays in correct direction BUT
		#we need to normalize to 96kHz
		for f in os.listdir(os.getcwd()): #for each file in the processing dir
			if f.endswith("-processed.wav") or f.endswith("-reversed.wav"):
				print "ffprobe and resample if necessary"
				output = subprocess.Popen("ffprobe -show_streams -of flat " + f,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
				ffdata,err = output.communicate()
				#grep the bit about the duiration, in seconds
				#for line in lines:
				match = ''
				sr = ''
				match = re.search(r".*sample_rate=.*",ffdata)
				if match:
					_sr = match.group().split('"')[1::2]
					sr = _sr[0]
				if not sr == "96000":
					output = subprocess.call("ffmpeg -i " + f + " -ar 96000 -c:a pcm_s24le " + f.replace(".wav","") + "-resampled.wav")
					print f
					if os.path.getsize(f.replace(".wav","") + "-resampled.wav") > 50000:
						os.remove(os.path.join(os.getcwd(),f))
					else:	
						return
	return

def ren(aNumber,captureDir,mmrepo):
	with cd(os.path.join(captureDir,aNumber)):
		for f in os.listdir(os.getcwd()):
			if "left" in f:
				if not os.path.exists("cusb-" + aNumber + "Aa.wav"):
					os.rename(f, "cusb-" + aNumber + "Aa.wav")
				else:
					os.rename(f, "cusb-" + aNumber + "Ca.wav")
			if "right" in f:
				if not os.path.exists("cusb-" + aNumber + "Ba.wav"):
					os.rename(f, "cusb-" + aNumber + "Ba.wav")
				else:
					os.rename(f, "cusb-" + aNumber + "Da.wav")
		for f in os.listdir(os.getcwd()):	
			match = ''
			match = re.search("\w{8}-\w{4}-\w{4}-\w{4}-",f)
			if match:
				if not os.path.exists("cusb-" + aNumber + "a.wav"):
					os.rename(f, "cusb-" + aNumber + "a.wav")
	return
	
#do the fancy library thing to each file	
def bextprocess(aNumber,bextsDir,captureDir):
	dirNumber = aNumber
	if aNumber.endswith("A") or aNumber.endswith("B") or aNumber.endswith("C") or aNumber.endswith("D"):
		dirNumber = aNumber[:-1]
	processingDir = os.path.join(captureDir,dirNumber)
	endObj1 = os.path.join(processingDir,"cusb-" + aNumber + "a.wav")
	endObj1A = os.path.join(processingDir,"cusb-" + aNumber + "Aa.wav")
	endObj1B = os.path.join(processingDir,"cusb-" + aNumber + "Ba.wav")
	endObj1C = os.path.join(processingDir,"cusb-" + aNumber + "Ca.wav")
	endObj1D = os.path.join(processingDir,"cusb-" + aNumber + "Da.wav")
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
	if os.path.exists(endObj1C):
		subprocess.call('bwfmetaedit --in-core-remove ' + endObj1C)
		subprocess.call('bwfmetaedit --MD5-Embed-Overwrite ' + endObj1C)
	if os.path.exists(endObj1D):
		subprocess.call('bwfmetaedit --in-core-remove ' + endObj1D)
		subprocess.call('bwfmetaedit --MD5-Embed-Overwrite ' + endObj1D)
	
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
			if os.path.exists(endObj1A):
				subprocess.call('bwfmetaedit ' + bextstr + ' ' + endObj1A)
			if os.path.exists(endObj1B):
				subprocess.call('bwfmetaedit ' + bextstr + ' ' + endObj1B)
			if os.path.exists(endObj1C):
				subprocess.call('bwfmetaedit ' + bextstr + ' ' + endObj1C)
			if os.path.exists(endObj1D):
				subprocess.call('bwfmetaedit ' + bextstr + ' ' + endObj1D)
	return

#hashmove processing folder to the repo	
def move(rawfname,aNumber,captureDir,mmrepo,archRepoDir):
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
		output = subprocess.Popen(['python',os.path.join(mmrepo,'hashmove.py'),processingDir,endDir],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		foo,err = output.communicate()
		print foo
		sourcehash = re.search('srce\s\S+\s\w{32}',foo)
		desthash = re.search('dest\s\S+\s\w{32}',foo)
		dh = desthash.group()
		sh = sourcehash.group()
		bexttxt = os.path.join("R:/audio/avlab/fm-exports/bexttxts","cusb-" + dirNumber + "-bext.txt")
		startObj1 = os.path.join("R:/audio/avlab/fm-exports/to_process",rawfname + ".txt")
		if sh[-32:] == dh[-32:]:
			os.remove(os.path.join(captureDir,rawfname + ".wav"))
			if os.path.exists(bexttxt): #can't give os.remove a file object it's gotta be a string grrrrr
				os.remove(os.path.join("R:/audio/avlab/fm-exports/bexttxts","cusb-" + dirNumber + "-bext.txt"))
			if os.path.exists(startObj1):
				os.remove(os.path.join("R:/audio/avlab/fm-exports/to_process",rawfname + ".txt"))
	return

def main():
	#initialize the stuff
	parser = argparse.ArgumentParser(description="slices, reverses input file, concatenates back together")
	parser.add_argument('-s',action="store_true",default=False,help='single mode, for processing a single transfer')
	parser.add_argument('-i','--input',help="the aNumber to process")
	args = vars(parser.parse_args())
	config = ConfigParser.ConfigParser()
	dn, fn = os.path.split(os.path.abspath(__file__)) #grip the path to the directory where ~this~ script is located
	config.read(os.path.join(dn,"microservices-config.ini"))
	captureDir = config.get('magneticTape','new_ingest')
	archRepoDir = config.get('magneticTape','repo')
	avlab = config.get('magneticTape','avlab')
	bextsDir = config.get('magneticTape','bexttxts')
	toProcessDir = config.get('magneticTape','to_process')
	scratch = config.get('magneticTape','scratch')
	mmrepo = config.get('global','scriptRepo')
	
	#get rid of the crap
	#deletebs(captureDir)
	
	#single mode check
	if args['s'] is True:
		flist = {}
		number = args['input'].replace("a","")
		for dirs, subdirs, files in os.walk(toProcessDir):
			for f in files:
				if not f.endswith(".txt"): #SOMETIMES FILEMAKER DOESN'T EXPORT THE .TXT PART BECAUSE IT'S GREAT AND I LOVE IT
					f = f + ".txt"
				rawfname,ext = os.path.splitext(f) #grab raw file name from os.walk
				txtinfo = os.path.join(toProcessDir,rawfname + '.txt') #init var for full path of txt file that tells us how to process
				if os.path.exists(txtinfo): #if said text file exists
					with open(txtinfo) as arb:
						fulline = csv.reader(arb, delimiter=",") #use csv lib to read it line by line
						for x in fulline: #result is list
							if x[0] == number:
								flist[rawfname] = x #makes dict of rawfilename : [anumber(wihtout the 'a'),track configuration] values
		for rawfname,process in flist.iteritems():
			if os.path.exists(os.path.join(captureDir,rawfname + ".wav")):
				aNumber = args['input']
				ffprocess(aNumber,rawfname,process,captureDir,toProcessDir,mmrepo)
				ren(aNumber,captureDir,mmrepo)
	else:
		#check for files that are too large
		for f in os.listdir(captureDir):
			if f.endswith(".wav"):
				if os.path.getsize(os.path.join(captureDir,f)) > 4294967296:
					subprocess.call(["python",os.path.join(mmrepo,"hashmove.py"),os.path.join(captureDir,f),os.path.join(scratch,"toobig")])
		
		#make a list of files to work on
		flist = makelist(captureDir,toProcessDir)

		for rawfname, process in flist.iteritems():
			if os.path.exists(os.path.join(captureDir,rawfname + ".wav")):
				aNumber = "a" + process[0]

				#run the ffmpeg stuff we gotta do (silence removal, to add: changechannels and splitfiles)
				ffprocess(aNumber,rawfname,process,captureDir,toProcessDir,mmrepo)
				
				#give comp time to catch up
				time.sleep(2)
				
				#rename the outputs from ffprocess
				ren(aNumber,captureDir,mmrepo)
				
				#pop the bext info into each file
				bextprocess(aNumber,bextsDir,captureDir)

				#hashmove them to the repo dir
				move(rawfname,aNumber,captureDir,mmrepo,archRepoDir)
	return

dependencies()
main()
