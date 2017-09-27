'''
makes a start object full path based on supplied canonical name
prioritizes broadcast wav
e.g.:
cusb-a1234 -> R:/audio/1000/a1234/cusb-a1234a.wav
cusb_col_a123_01_456_00 -> R:/78rpm/repo/cusb_col_a123_01_456_00/cusb_col_a123_01_456_00.wav
cyl1234 -> R:/Cylinders/1000/1234/cusb-cyl1234b.wav
'''
import os
import re
import argparse
import sys
###UCSB modules###
import config as rawconfig
import util as ut


def avname(startObj, avlist):
	'''
	makes and SO for AV names - magnetic audio tape and video
	'''
	if "v" in startObj:
		for dirs, subdirs, files in os.walk(avlist[1]):
			for s in subdirs:
				if startObj in s:
					print "found video " + startObj + " in subdir " + os.path.join(dirs, s)
					return startObj
		for dirs, subdirs, files in os.walk(avlist[2]):
			for s in subdirs:
				if startObj in s:
					print "found video " + startObj + " in subdir " + os.path.join(dirs, s)
					return startObj
	else:
		canonSO = startObj.replace("cusb-", "")
		aNumber = canonSO.replace("a", "") #input arg here is a1234 but we want just the number
		face = ''
		match = ''
		match = re.search(r"\D\Z", aNumber)
		if match:
			face = match.group()
			aNumber = aNumber.replace(face, "")	
		#the following separates out the first digit and assigns an appropriate number of zeroes to match our dir structure
		if len(aNumber) < 5:
			endDirThousand = aNumber[:1] + "000"
		else:
			endDirThousand = aNumber[:2] + "000"
		soContainingDir = os.path.join(avlist[0], endDirThousand, canonSO.replace(face, ""))
		#print soContainingDir
		if os.path.exists(soContainingDir):
			with ut.cd(soContainingDir):
				#print os.getcwd()
				if os.path.exists("cusb-a" + aNumber + face + "b.wav"):
					startObj = os.path.join(os.getcwd(), "cusb-a" + aNumber + face + "b.wav")
					return startObj
				elif os.path.exists("cusb-a" + aNumber + face + "a.wav"):
					startObj = os.path.join(os.getcwd(), "cusb-a" + aNumber + face + "a.wav")
					return startObj
				elif os.path.exists("cusb-a" + aNumber + face + ".wav"):
					startObj = os.path.join(os.getcwd(), "cusb-a" + aNumber + face + ".wav")	
					return startObj
				else:
					return soContainingDir
		else:
			print "Buddy, the directory " + soContainingDir + " doesn't exist. This asset has probably not yet been digitized"
		
		
def cylname(startObj, cyllist):	
	'''
	in process
	'''
	return startObj
	
def discname(startObj, disclist):
	'''
	makes start object for disc
	'''
	foundirs = []
	for dirpath in disclist:
		if os.path.exists(os.path.join(dirpath, startObj)):
			foundirs.append(os.path.join(dirpath, startObj))
	if len(foundirs) > 1:
		print "Buddy, it looks like there's two copies of this item"
		for f in foundirs:
			print f
		sys.exit()	
	elif len(foundirs) < 1:
		print "Buddy, it looks like this hasn't been digitized"
		sys.exit()
	else:
		startDir = foundirs[0]
	if os.path.exists(os.path.join(startDir, startObj + "b.wav")):
		startObj = os.path.join(startDir, startObj + "b.wav")
		return startObj
	elif os.path.exists(os.path.join(startDir, startObj + ".wav")):
		startObj = os.path.join(startDir, startObj + ".wav")
		return startObj
	elif os.path.exists(os.path.join(startDir, startObj + "a.wav")):
		startObj = os.path.join(startDir, startObj + "a.wav")
		return startObj
		
def parse_input(startObj):
	'''
	parses input to find type of object for which to make a start object
	'''
	allists = make_lists()
	match=''
	match=re.search(r"\w\:\/", startObj)
	if match:
		#print "it's a fullpath"
		return startObj
	match=''
	match=re.search(r"^cusb-(a|v)\d+", startObj)
	if match:
		#print "it's a cusb-AVassetname"
		startObj = avname(startObj, allists['avlist'])
		return startObj
	match=''
	match=re.search(r"^(a|v)\d+", startObj)
	if match:
		#print "it's a canonical AVassetname"
		startObj = avname(startObj, allists['avlist'])
		return startObj
	match=''
	match=re.search(r"^cusb_", startObj)
	if match:
		#print "it's a disc"
		startObj = discname(startObj, allists['disclist'])
		return startObj
	match=''
	match=re.search(r"^cusb-cyl\d+", startObj)
	if match:
		#print "it's a cusb-cylindername"
		startObj = cylname(startObj, allists['cylist'])
		return startObj
	match=''
	match=re.search(r"^^(C|c)yl(inder\d+|\d+)", startObj)
	if match:
		#print "it's a canonical cylindername"
		startObj = cylname(startObj, allists['cylist'])
		return startObj

def make_lists():
	'''
	makes the lists of folder paths to search for a start object
	'''
	global conf
	conf = rawconfig.config()
	tapeRepoDir = conf.magneticTape.repo
	tapeNewIngest = conf.magneticTape.new_ingest
	cylinderRepoDir = conf.cylinders.repo
	cylinderNewIngest = conf.cylinders.new_ingest
	discRepoDir = conf.discs.repo
	discNewIngest = conf.discs.new_ingest
	discNewIngest = conf.discs.PreIngestQCDir
	njBroadDir = conf.NationalJukebox.AudioBroadDir
	njPreIngestDir = conf.NationalJukebox.PreIngestQCDir
	videoRepoDir = conf.video.repo
	videoNewIngest = conf.video.new_ingest
	avlist = [tapeRepoDir, videoNewIngest, videoRepoDir,tapeNewIngest]
	cylist = [cylinderNewIngest, cylinderRepoDir]
	disclist = [discNewIngest, njBroadDir, njPreIngestDir, discRepoDir]
	allists={}
	allists["avlist"]=avlist
	allists["cylist"]=cylist
	allists["disclist"]=disclist
	return allists

def main():
	'''
	do the thing
	'''
	###INIT VARS###
	parser = argparse.ArgumentParser(description="makes a full path from a canonical asset name")
	parser.add_argument('-i', '--input', dest='i', nargs ='?', help='the object, can be full path or assetname, e.g. a1234, cusb_col_a123_01_456_00')
	args = parser.parse_args()
	allists = make_lists()
	###END INIT###
	startObj = args.i.replace("\\", '/') #for the windows peeps
	startObj = parse_input(startObj)
	#print len(startObj)
	print startObj

if __name__ == "__main__":
	main()		