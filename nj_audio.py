#!/usr/bin/env python
#nj_audio.py
#processes audio fles for the national jukebox project at UCSB

import os
import sys
import getpass
import time
import imp
import subprocess
from distutils import spawn

#check that we have the required software to run this script
def dependencies():
	depends = ['ffmpeg','ffprobe','bwfmetaedit']
	for d in depends:
		if spawn.find_executable(d) is None:
			print "Buddy, you gotta install " + d
			sys.exit()
	return		

	
def main():
	###INIT STUFF###
	dn, fn = os.path.split(os.path.abspath(__file__)) #grip the path to the directory where ~this~ script is located
	global log
	log = imp.load_source('log',os.path.join(dn,'logger.py'))
	log.log("started")
	global ut
	ut = imp.load_source('util',os.path.join(dn,'util.py'))
	global conf
	rawconfig = imp.load_source('config',os.path.join(dn,'config.py'))
	conf = rawconfig.config()
	qcDir = conf.NationalJukebox.PreIngestQCDir
	batchDir = conf.NationalJukebox.BatchDir
	archDir = conf.NationalJukebox.AudioArchDir
	broadDir = conf.NationalJukebox.AudioBroadDir
	barcode = sys.argv[1] #grab the lone argument that FM provides
	_fname = barcode + ".wav"
	if not os.path.exists(os.path.join(archDir,_fname)) or not os.path.exists(os.path.join(broadDir,_fname)):
		log.log(**{"message":"file " + _fname + " missing from arch or broad dir, not processed","level":"error"})
		print "File " + _fname + " missing from arch or broad directory and was not processed"
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
			log.log(**{"message":"attempt to process " + fname + " timed out","level":"warning"})
			print "Processing of file " + fname + " has timed out because this file remains open in another program"
			print "Please check that this file is closed in Wavelab"
			foo = raw_input("To re-try processing, uncheck and re-check the 'transferred' box on this matrix's FileMaker record")
			sys.exit()
		###END VERIFY###
		
	###END INIT###
	log.log("timeDiff = " + str(timeDiff))
	###make broadcast master###
	output = subprocess.check_output(['python',os.path.join(conf.scriptRepo,'makebroadcast.py'),'-i',broadcastFP,'-ff','-nj'],stderr=subprocess.STDOUT) #makebroadcast with fades, nj naming
	log.log(output)
	#pop them into the qc dir in a subdir named after their filename
	#hashmove makes end dir if it doesnt exist already
	output = subprocess.check_output(['python',os.path.join(conf.scriptRepo,'hashmove.py'),broadcastFP,os.path.join(qcDir,barcode)])
	log.log(output)
	###end make broadcast master###
	###make archive master###
	os.rename(archiveFP_pre,archiveFP_post)
	log.log("file " + archiveFP_pre + "renamed " + archiveFP_post)
	#embed an md5 hash in the md5 chunk
	subprocess.call(['bwfmetaedit','--in-core-remove',archiveFP_post])
	subprocess.call(['bwfmetaedit','--MD5-Embed',archiveFP_post])
	#move them to qc dir in subdir named after their canonical filename (actual file name has "m" at end)
	output = subprocess.check_output(['python',os.path.join(conf.scriptRepo,'hashmove.py'),archiveFP_post,os.path.join(qcDir,barcode)])
	log.log(output)
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

dependencies()
main()
log.log("complete")