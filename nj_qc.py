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

def makelist(qcDir, batchDir, extlist,mmrepo,scratch):
	dirlist = []
	#make a list of dirs that have everything we need
	for dirs, subdirs, files in os.walk(qcDir): #loop thru qc dir
		for s in subdirs: #loop thru each subdir
			print "Verifying contents of " + s
			if os.path.exists(os.path.join(batchDir,s)): #if it already exsists in our dest that's bad figure it out
				subprocess.call(['python',os.path.join(mmrepo,"hashmove.py"),os.path.join(dirs,s),os.path.join(scratch,s)])
			#ok, dirs that make it here aren't in our batch dir already
			else:
				with cd(os.path.join(dirs,s)): #cd into each subdir
					if os.path.isfile(s + extlist[0]) and os.path.isfile(s + extlist[1]) and os.path.isfile(s + extlist[2]): #if each file extension exists in there
						dirlist.append(s) #append the subdir to the list of files we wanna move
	return dirlist
		
def main():
	#initialize from the config file
	config = ConfigParser.ConfigParser()
	dn, fn = os.path.split(os.path.abspath(__file__)) #grip the path to the directory where ~this~ script is located
	config.read(os.path.join(dn,"microservices-config.ini"))
	qcDir = config.get('NationalJukebox','PreIngestQCDir')
	batchDir = config.get('NationalJukebox','BatchDir')
	mmrepo = config.get('global','scriptRepo')
	scratch = config.get('NationalJukebox','scratch')
	extlist = ['m.wav','.wav','.tif']

	subprocess.call(['python',os.path.join(mmrepo,'rename_ucsbtocusb.py'),qcDir]) #rename them from ucsb to cusb
	
	dirlist = makelist(qcDir, batchDir, extlist,mmrepo,scratch)
	
	#now move them
	for d in dirlist: #for each verified subdir
		print os.path.join(batchDir,d)
		subprocess.call(['python',os.path.join(mmrepo,'hashmove.py'),os.path.join(qcDir,d),os.path.join(batchDir,d)]) #hashmove it to the batch folder
				
	return

main()