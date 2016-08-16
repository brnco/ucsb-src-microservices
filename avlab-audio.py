#avlab-magneticTape

import ConfigParser
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
	ffmpeglist = ffmpegstring.split()
	if not os.path.exists(processDir):
		os.makedirs(processDir)
	with cd(processDir):
		returncode = 0
		try:
			output = subprocess.check_output(ffmpeglist,shell=True)
			returncode = 0
		except subprocess.CalledProcessError,e:
			output = e.output
			returncode = output
		if returncode == 0:
			os.remove(os.path.join(captureDir,rawfname + ".wav"))
		else:
			return
			
		revstr0 = ''
		revstr1 = ''
		revstr01 = ''
		match = ''
		#check for reverse
		if "rev_fA" in process:
			revstr0 = ",areverse"
		if "rev_fC" in process:
			revstr0 = ",areverse"
		if "rev_fB" in process:
			revstr1 = ",areverse"
		if "rev_fD" in process:
			revstr1 = ",areverse"
		if "rev_fAB" in process:
			revstr01 = ',areverse'
		if 'rev_fCD' in process:
			revstr01 = ',areverse'
		if 'rev_str01':
			subprocess.call(['python',os.path.join(mmrepo,"makereverse.py"),rawfname + "-processed.wav"])
		if 'rev_str0':
			subprocess.call(['python',os.path.join(mmrepo,"makereverse.py"),"left.wav"])
		if 'rev_str1':
			subprocess.call(['python',os.path.join(mmrepo,"makereverse.py"),"right.wav"])
		
		#ok so by now every file is correct BUT
		#we need to normalize to 96kHz
		for f in os.listdir(os.getcwd()): #for each file in the processing dir
			if f.endswith("-processed.wav") or f.endswith("-reversed.wav"):
				print "ffprobe and resample if necessary"
		
	return

#do the fancy library thing to each file	
def bextprocess(aNumber,bextsDir,captureDir):
	dirNumber = aNumber
	if aNumber.endswith("A") or aNumber.endswith("B"):
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
	config = ConfigParser.ConfigParser()
	dn, fn = os.path.split(os.path.abspath(__file__)) #grip the path to the directory where ~this~ script is located
	config.read(os.path.join(dn,"microservices-config.ini"))
	captureDir = config.get('magneticTape','new_ingest')
	archRepoDir = config.get('magneticTape','repo')
	avlab = config.get('magneticTape','avlab')
	bextsDir = config.get('magneticTape','bexttxts')
	toProcessDir = config.get('magneticTape','to_process')
	mmrepo = config.get('global','scriptRepo')
	#htm-update test
	#get rid of the crap
	#deletebs(captureDir)

	#make a list of files to work on
	flist = makelist(captureDir,toProcessDir)

	for rawfname, process in flist.iteritems():
		aNumber = "a" + process[0]

		#run the ffmpeg stuff we gotta do (silence removal, to add: changechannels and splitfiles)
		#try:
		ffprocess(aNumber,rawfname,process,captureDir,toProcessDir,mmrepo)
		
			#pop the bext info into each file
			#bextprocess(aNumber,bextsDir,captureDir)

			#hashmove them to the repo dir
			#move(rawfname,aNumber,captureDir,mmrepo,archRepoDir)
		#except:
			#pass
		foo = raw_input("eh")
	return

dependencies()
main()
