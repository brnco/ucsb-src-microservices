'''
#nj_audio.py
#processes audio files for the national jukebox project at UCSB
'''
import os
import sys
import getpass
import time
import subprocess
import argparse
###UCSB modules###
import config as rawconfig
import util as ut
from logger import log
import mtd
import makestartobject as makeso

def main():
	'''
	do the thing
	'''
	log("started")
	global conf
	conf = rawconfig.config()
	parser = argparse.ArgumentParser(description="processes disc transfers for NJ project")
	parser.add_argument("input",help="the barcode of the disc you'd like to process")
	args = parser.parse_args()
	qcDir = conf.NationalJukebox.PreIngestQCDir
	batchDir = conf.NationalJukebox.BatchDir
	archDir = conf.NationalJukebox.AudioArchDir
	broadDir = conf.NationalJukebox.AudioBroadDir
	barcode = args.input #grab the lone argument that FM provides
	_fname = barcode + ".wav"
	log(**{"message":"processing " + barcode,"print":True})
	if not os.path.exists(os.path.join(archDir,_fname)) or not os.path.exists(os.path.join(broadDir,_fname)):
		log(**{"message":"file " + _fname + " missing from arch or broad dir, not processed","level":"error","print":True})
		#print "Please check that you saved the file to the right directory in Wavelab before indicating that it was transferred"
		foo = raw_input("Please check that the file was named correctly and saved to the correct directory")
		sys.exit()
	else:	
		barcode = barcode.replace("ucsb","cusb") #stupid, stupid bug
		fname = barcode + ".wav"
		archive_fname = barcode + "m.wav" #make the new filename 
		broadcast_fname = barcode + ".wav"
		archiveFP_pre = os.path.join(archDir,fname)
		archiveFP_post = os.path.join(archDir,archive_fname)
		broadcastFP = os.path.join(broadDir,fname)
		###VERIFY WE CAN WORK ON THIS FILE###
		startTime = time.time()
		timeDiff = time.time() - startTime
		#try to rename it once every 3mins for 15mins
		#this basically waits for the user to close this file in Wavelab
		while timeDiff < 900:
			try:
				if os.path.exists(os.path.join(archDir,_fname)):
					os.rename(os.path.join(archDir,_fname),archiveFP_pre) #changes filenames to cusb
				if os.path.exists(os.path.join(broadDir,_fname)):
					os.rename(os.path.join(broadDir,_fname),broadcastFP)
				elif not os.path.exists(archiveFP_pre) or not os.path.exists(broadcastFP):
					print "buddy, something went wrong"
					sys.exit()
				else:	
					break
			except OSError,e:
				time.sleep(60)
				timeDiff = time.time() - startTime		
		if timeDiff	>= 900.0:
			log(**{"message":"attempt to process " + fname + " timed out because this file is open in another program","level":"warning","print":True})
			log(**{"message":"Please check that this file is closed in Wavelab","print":True})
			foo = raw_input("To re-try processing, uncheck and re-check the 'transferred' box on this matrix's FileMaker record")
			sys.exit()
		###END VERIFY###
		
	###END INIT###
	log("timeDiff = " + str(timeDiff))
	###make broadcast master###
	output = subprocess.check_output(['python',os.path.join(conf.scriptRepo,'makebroadcast.py'),'-i',broadcastFP,'-ff','-nj'],stderr=subprocess.STDOUT) #makebroadcast with fades, nj naming
	log(output)
	#pop them into the qc dir in a subdir named after their filename
	#hashmove makes end dir if it doesnt exist already
	output = subprocess.check_output(['python',os.path.join(conf.scriptRepo,'hashmove.py'),broadcastFP,os.path.join(qcDir,barcode)])
	log(output)
	###end make broadcast master###
	###make archive master###
	os.rename(archiveFP_pre,archiveFP_post)
	log("file " + archiveFP_pre + "renamed " + archiveFP_post)
	#embed an md5 hash in the md5 chunk
	subprocess.call(['bwfmetaedit','--in-core-remove',archiveFP_post])
	subprocess.call(['bwfmetaedit','--MD5-Embed',archiveFP_post])
	#move them to qc dir in subdir named after their canonical filename (actual file name has "m" at end)
	output = subprocess.check_output(['python',os.path.join(conf.scriptRepo,'hashmove.py'),archiveFP_post,os.path.join(qcDir,barcode)])
	log(output)
	###end make archive master###
	###delete bs###
	with ut.cd(archDir):
		for dirs, subdirs, files in os.walk(os.getcwd()):
			for f in files:
				if f.endswith(".gpk") or f.endswith(".mrk"):
					try:
						os.remove(f)
					except:
						pass
	with ut.cd(broadDir):
		for dirs, subdirs, files in os.walk(os.getcwd()):
			for f in files:
				if f.endswith(".gpk") or f.endswith(".bak") or f.endswith(".mrk"):
					try:
						os.remove(f)
					except:
						pass					
	###end delete bs###

if __name__ == '__main__':
	main()
	log("complete")