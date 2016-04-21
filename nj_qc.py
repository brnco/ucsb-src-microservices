#nj_QC
#verifies that all relevant filetypes exist (and, one day, conform) to NJ SIP
#takes no args
#has no dependencies

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

def main():
	#initialize from the config file
	config = ConfigParser.ConfigParser()
	config.read("C:/Users/" + getpass.getuser() + "/microservices-config.ini")
	qcDir = config.get('NationalJukebox','PreIngestQCDir')
	batchDir = config.get('NationalJukebox','BatchDir')
	mmrepo = config.get('global','scriptRepo')
	flist = ['m.wav','.wav','.tif']
	dirlist = []
	with cd(qcDir):
		subprocess.call(['python',os.path.join(mmrepo,'rename_ucsbtocusb.py'),qcDir])
	#make a list of dirs that have everything we need
	for dirs, subdirs, files in os.walk(qcDir): #loop thru qc dir
		for s in subdirs: #loop thru each subdir
			print "Verifying contents of " + s
			if os.path.exists(os.path.join(batchDir,s)): #if it already exsists in our dest that's real bad figure it out
				print "Buddy, check on this SIP: " + s
				print "It already exists in our batch directory"
				break
			with cd(os.path.join(dirs,s)): #cd into each subdir
				if os.path.isfile(s + flist[0]) and os.path.isfile(s + flist[1]) and os.path.isfile(s + flist[2]): #if each file extension exists in there
					dirlist.append(s) #append the subdir to the list of files we wanna move
	for d in dirlist: #for each verified subdir
		subprocess.call(['python',os.path.join(mmrepo,'hashmove.py'),os.path.join(qcDir,d),os.path.join(batchDir,d)]) #hashmove it to the batch folder
				
	return

main()