#one day this will take a canonical input eg:
#cusb_victor_123_01_456_00
#cusb-cyl1234
#cusb-v1234
#cusb-a1234Ba
#it'll take inputs like thsoe^^^^
#and it'll make the full path to that object

import os
import re
import ConfigParser
import argparse

#Context manager for changing the current working directory
class cd:
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

def avname(startObj,avlist):
	if "v" in startObj:
		for dirs,subdirs,files in os.walk(avlist[1]):
			for s in subdirs:
				if startObj in s:
					print "found video " + startObj + " in subdir " + os.path.join(dirs,s)
					return startObj
		for dirs,subdirs,files in os.walk(avlist[2]):
			for s in subdirs:
				if startObj in s:
					print "found video " + startObj + " in subdir " + os.path.join(dirs,s)
					return startObj
	else:
		canonSO = startObj.replace("cusb-","")
		aNumber = canonSO.replace("a","") #input arg here is a1234 but we want just the number
		#the following separates out the first digit and assigns an appropriate number of zeroes to match our dir structure
		if len(aNumber) < 5:
			endDirThousand = aNumber[:1] + "000"
		else:
			endDirThousand = aNumber[:2] + "000"
		soContainingDir = os.path.join(avlist[0],endDirThousand,canonSO)
		if os.path.exists(soContainingDir):
			with cd(soContainingDir):
				if os.path.exists("cusb-a" + aNumber + ".wav"):
					startObj = os.path.join(os.getcwd(),"cusb-a" + aNumber + ".wav")
				elif os.path.exists("cusb-a" + aNumber + "a.wav"):
					startObj = os.path.join(os.getcwd(),"cusb-a" + aNumber + "a.wav")
		else:
			print "Buddy, the directory " + soContainingDir + " doesn't exist. This asset has probably not yet been digitized"
		return startObj
		
def cylname(startObj,disclist):	
	return startObj
def discname(startObj,cylist):
	return startObj
	
def startObjectParse(startObj,allists):
	match=''
	match=re.search(r"\w\:\/",startObj)
	if match:
		#print "it's a fullpath"
		return startObj
	match=''
	match=re.search(r"^cusb-(a|v)\d+",startObj)
	if match:
		#print "it's a cusb-AVassetname"
		startObj = avname(startObj,allists['avlist'])
		return startObj
	match=''
	match=re.search(r"^(a|v)\d+",startObj)
	if match:
		#print "it's a canonical AVassetname"
		startObj = avname(startObj,allists['avlist'])
		return startObj
	match=''
	match=re.search(r"^cusb_",startObj)
	if match:
		#print "it's a disc"
		startObj = discname(startObj,allists['disclist'])
		return startObj
	match=''
	match=re.search(r"^cusb-cyl\d+",startObj)
	if match:
		#print "it's a cusb-cylindername"
		startObj = cylname(startObj,allists['cylist'])
		return startObj
	match=''
	match=re.search(r"^^(C|c)yl(inder\d+|\d+)",startObj)
	if match:
		#print "it's a canonical cylindername"
		startObj = cylname(startObj,allists['cylist'])
		return startObj

def main():
	config = ConfigParser.ConfigParser()
	dn, fn = os.path.split(os.path.abspath(__file__)) #grip the path to the directory where ~this~ script is located
	config.read(os.path.join(dn,"microservices-config.ini"))
	tapeRepoDir = config.get('magneticTape','repo')
	tapeNewIngest = config.get('magneticTape','new_ingest')
	cylinderRepoDir = config.get('cylinders','repo')
	cylinderNewIngest = config.get('cylinders','new_ingest')
	discRepoDir = config.get('discs','repo')
	discNewIngest = config.get('discs','new_ingest')
	njBroadDir = config.get('NationalJukebox','AudioBroadDir')
	njPreIngestDir = config.get('NationalJukebox','PreIngestQCDir')
	videoRepoDir = config.get('video','repo')
	videoNewIngest = config.get('video','new_ingest')
	avlist = [tapeRepoDir,videoNewIngest,videoRepoDir]
	cylist = [cylinderNewIngest,cylinderRepoDir]
	disclist = [discNewIngest,njBroadDir,njPreIngestDir,discRepoDir]
	allists={}
	allists["avlist"]=avlist
	allists["cylist"]=cylist
	allists["disclist"]=disclist
	parser = argparse.ArgumentParser(description="Makes a broadcast-ready file from a single input file. Only works for 'audio' assets at the moment, not discs or cylinders")
	parser.add_argument('-so','--startObj',dest='so',nargs ='?',help='the file to be transcoded, can be full path or assetname, e.g. a1234, cusb_col_a123_01_456_00')
	args = parser.parse_args()
	startObj = args.so.replace("\\",'/') #for the windows peeps
	startObj = startObjectParse(startObj,allists)
	print startObj
main()		