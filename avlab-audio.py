#avlab-magneticTape

import ConfigParser
import getpass
import os
import subprocess
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

#takes files rooted at capture dir
def makelist(captureDir,toProcessDir,flist = {}):
	for dirs, subdirs, files in os.walk(captureDir):
		for f in files:
			#grab fname, initialize variable anme for text file containing aNumber from FM
			fname,ext = os.path.splitext(f)
			txtinfo = os.path.join(toProcessDir,fname + '.txt')
			if os.path.exists(txtinfo):
				with open(txtinfo) as arb:
					opts = arb.readlines()
					opts = str(opts)
					foo = opts.strip("['']")
					bar = foo.replace(r"\n","")
					#sets up dict of raw-wavelab-output-name : aNumber-fromFM pairs
					flist[fname] = "a" + bar
	return flist

def ffprocess(flist,captureDir):
	for f in flist:
		aNumber = str(flist[f])
		processingDir = os.path.join(captureDir,aNumber)
		endObj1 = os.path.join(processingDir,"cusb-" + aNumber + "a.wav") #name of archival master when we're done
		#make a processing directory named after first attr in fm export: aNumber
		if not os.path.exists(processingDir):
			os.makedirs(processingDir)
			#remove silence from raw transfer if audio quieter than -50dB, longer than 10s of silence
		subprocess.call('ffmpeg -i ' + os.path.join(captureDir,f) + '.wav -af silenceremove=0:0:-50dB:-10:1:-50dB -acodec pcm_s24le ' + endObj1) 
		
		#NOT FULLY IMPLEMENTED
		with cd(processingDir):
			#changechannels call
				#loop through flist dict
				#for each[key] do values
				#reverse if necessary
				#delte after split if necessary
				
			#split files larger than 2GB	
			statinfo = os.stat(endObj1)
			eo1size = statinfo.st_size
			if eo1size >= 2147483648:
				print "too big too wide"
	return

def bextprocess(flist,bextsDir,captureDir):
	for f in flist:
		aNumber = str(flist[f])
		processingDir = os.path.join(captureDir,aNumber)
		endObj1 = os.path.join(processingDir,"cusb-" + aNumber + "a.wav")
		#clear mtd already in there
		subprocess.call('bwfmetaedit --in-core-remove ' + endObj1)
		#embed checksums
		subprocess.call('bwfmetaedit --MD5-Embed-Overwrite ' + endObj1)
		#embed bext metadata based on FM output
		bextFile = os.path.join(bextsDir,'cusb-' + aNumber + '-bext.txt')
		with open(bextFile) as bf:
			bextlst = bf.readlines()
			bextstr = str(bextlst)
			bextstr = bextstr.strip("['']")
			subprocess.call('bwfmetaedit ' + bextstr + ' ' + endObj1)
	return

def move(flist,captureDir,mmrepo,archRepoDir):
	for f in flist:
		aNumber = str(flist[f])
		processingDir = os.path.join(captureDir,aNumber)
		endDirThousand = aNumber.replace("a","") #input arg here is a1234 but we want just the number
		#the following separates out the first digit and assigns an appropriate number of zeroes to match our dir structure
		if len(endDirThousand) < 5:
			endDirThousand = endDirThousand[:1] + "000"
		else:
			endDirThousand = endDirThousand[:2] + "000"
		endDir = os.path.join(archRepoDir,endDirThousand,aNumber)
		subprocess.call(['python',os.path.join(mmrepo,'hashmove.py'),processingDir,endDir])
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
	ffprocess(flist,captureDir)
	
	#pop the bext info into each file
	bextprocess(flist,bextsDir,captureDir)
	
	#hashmove them to the repo dir
	move(flist,captureDir,mmrepo,archRepoDir)
	
	return

dependencies()
main()