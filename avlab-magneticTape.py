#avlab-magneticTape

import ConfigParser
import getpass
import os
import subprocess

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
			fname,ext = os.path.splitext(f)
			txtinfo = os.path.join(toProcessDir,fname + '.txt')
			if os.path.exists(txtinfo):
				with open(txtinfo) as f:
					opts = f.readlines()
					flist[fname] = opts
	return flist

def ffprocess(flist,captureDir):
	#make a processing directory named after first attr in fm export: aNumber
	for f in flist:
		aNumber = str(flist[f])
		aNumber = aNumber.strip("['']")
		processingDir = os.path.join(captureDir,aNumber)
		endObj1 = os.path.join(processingDir,"cusb-" + aNumber + "a.wav")
		if not os.path.exists(processingDir):
			os.makedirs(processingDir)
		#subprocess.call('ffmpeg -i ' + os.path.join(captureDir,f) + '.wav -af silenceremove=0:0:-50dB:-10:1:-50dB -acodec pcm_s24le ' + endObj1) 
		#print 'ffmpeg -i ' + f + '.wav -af silenceremove=0:0:-50dB:-10:1:-50dB -acodec pcm_s24le ' + os.path.join(processingDir,"cusb-" + aNumber + "a.wav")
		with cd(processingDir):
			statinfo = os.stat(endObj1)
			eo1size = statinfo.st_size
			if eo1size >= 2147483648:
				print "too big too wide"
	
	#silenceremove
	#ffmpeg -i [input] -af silenceremove=0:0:-50dB:-10:1:-50dB -acodec pcm_s24le [output]
	
	#changechannels call
		#loop through flist dict
		#for each[key] do values
		#reverse if necessary
		#delte after split if necessary
	
	#split files larger than 2GB
	
	return

def bextprocess(flist):
	#embed checksums
	#embed bext metadata based on FM output
	#renames based on FM output
	#hash them somehow
	return

def main():
	#initialize a capture directory
	config = ConfigParser.ConfigParser()
	config.read("C:/Users/" + getpass.getuser() + "/microservices-config.ini")
	captureDir = config.get('magneticTape','magTapeCaptureDir')
	repoDir = config.get('magneticTape','magTapeArchDir')
	toProcessDir = config.get('magneticTape','magTapeToProcessDir')
	logDir = config.get('magneticTape','magTapeLogs')
	mmrepo = config.get('global','scriptRepo')
	
	flist = makelist(captureDir,toProcessDir)
	
	ffprocess(flist,captureDir)
	
	return

main()