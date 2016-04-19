#makevideoSIP
#takes argument for video package (folder, named vNum)
#verifies all contents of SIP exist: -pres.mxf and -acc.mp4 files, -pres.mxf.PBCore2.0.xml metadata, -pres.mxf.framemd5 hash, -pres.qctools.xml.gz report, -pres.mxf.md5 and -acc.mp4.md5 hashes
#copies -acc.mp4 and ancillary data to vNumber folder on R:/
#gzips video package folder package
#logs manifest of all files present in SIP, hash of gzip, and assigns packageID
#-lto writes this data to our lto drive, logs the barcode of the lto tape

import os
import subprocess
import sys
import glob
import re
import argparse
import shutil
import tarfile
import gzip

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
	
def main():
	#parser
	parser = argparse.ArgumentParser(description="Makes the SIP for a video package, adds to lto stage and crates log")
	parser.add_argument('vNum',nargs ='?',help='The vNum directory to be SIPped',)
	#parser.add_argument('-ff','--fades',action='store_true',help='adds 2s heads and tails fades to black/ silence')
	#parser.add_argument('-s','--stereo',action='store_true',help='outputs to stereo (mono is default)')
	args = vars(parser.parse_args()) #create a dictionary instead of leaving args in NAMESPACE land
	vNum = args['vNum']
	v = vNum[1:]
	startObj = 'R:/Visual/avlab/new_ingest/' + vNum
	endObj = 'R:/Visual/0000/' + vNum
	if not os.path.isdir(startObj):
		print "Buddy, that's not a directory"
		sys.exit()
	if not os.path.exists(endObj):
		os.makedirs(endObj)
	#verify that all the right extensions are in there	
	with cd(startObj):
		extList = ['-pres.mxf','-acc.mp4','-pres.mxf.PBCore2.xml','-pres.mxf.framemd5','-pres.mxf.md5','-pres.mxf.qctools.xml.gz',]
		flist = []
		for file in os.listdir(startObj): #mak a list of the files in our startdir
			flist.append(file)
		for x in extList: #loop through boths lists that we made and if anything is missing say so
			if not any(x in f for f in flist): 
				print "Buddy, you're missing a sidecar file with a " + x + " extension"
				sys.exit()
		manifest = open(vNum + '-manifest.txt','w') #initialize a text file that we'll use to log what ~should~ be in this folder
		for f in flist:
			manifest.write(f + "\n")
		manifest.close()
		#copy to the access repo in R:/Visual
		for f in flist:
			if not f.endswith('.mxf'): #don't copy the preservation master
				print "Copying " + f
				shutil.copy2(f,endObj) #copy2 grabs the registry metadata which is cool and good
	#turn it into a tarball then gzip it
	with cd('R:/Visual/avlab/new_ingest/'):
		tar = tarfile.open(vNum + ".tar.gz","w:gz")
		tar.add(startObj)
		tar.close()
	return

main()