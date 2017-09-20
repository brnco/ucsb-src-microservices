#!/usr/bin/env python
#for pres mxf wrapped j2k files
#qctoolsreport
#pbcore2
#framemd5
#send acc + presmtd to R:\Visual\[0000]

import os
import subprocess
import sys
import re
import shutil
import argparse
###UCSB modules###
import config as rawconfig
import util as ut
import logger as log
import mtd
import makestartobject as makeso

def make_sidecar_qctools(sfull,canonicalName):
	#instantiate var names of our output files
	_qctfile = os.path.join(sfull,canonicalName + 'mxf.qctools.xml.gz')
	#_framemd5 = os.path.join(sfull,canonicalName + 'mxf.framemd5')
	#if there's not a qctools doc for it, make one
	print _qct
	if not os.path.exists(_qctfile):
		try:
			output = subprocess.check_output([conf.python,os.path.join(conf.scriptRepo,'makeqctoolsreport.py'),'-so',canonicalName + "-pres.mxf"])
			print output
			rtncode = 0
		except subprocess.CalledProcessError,e:
			rtncode = e
		return rtncode
		
	

def make_sidecar_mediainfo(sfull, canonicalName):
	_pbc2file = os.path.join(sfull,canonicalName + 'mxf.PBCore2.xml')
	#if there's not a PBCore2 doc for it, make one
	if not os.path.exists(_pbc2file):
		#gotta give the PBCore2 filename as concat string here, _pbc2file is a file object
		try:
			output = subprocess.check_output(['MediaInfo','--Output=PBCore2','--LogFile=' + _pbc2file,canonicalName + "-pres.mxf"])
			print output
			rtncode = 0
		except subprocess.CalledProcessError,e:
			rtncode = e
		return

def make_sidecar_framemd5(sfull,canonicalName):
	#if there's not a framemd5 for it, make one
	#if not os.path.exists(_framemd5):
	#gotta give the framemd5 filename as concat string here, _framemd5 is a file object
	subprocess.call(['ffmpeg','-i',presfile,'-f','framemd5',presfile + '.framemd5'])

#checks that uploads from the opencube are complete and good
def verify_opencube_upload(sfull,canonicalName):
	filetypes = ["-pres.mxf","-acc.mp4"] #required filetypes
	for f in filetypes:
		fullf = os.path.join(sfull,canonicalName + f)
		print fullf
		if not os.path.exists(fullf):
			print "missing file " + fullf
			return False
		if not os.path.exists(fullf + ".md5"):
			print "make a hash for " + fullf
			return False
	return True		

def frameRate_Original_bug_check(s1,fullpath):
	fro_bug_str = 'fail! ' + fullpath + '''
   --  [fail:master_format_policy.mxf]
   --   [fail:Video/FrameRate_Original is 59.940]'''
	remove = string.punctuation + string.whitespace
	return s1.translate(None, remove) == fro_bug_str.translate(None, remove)

def verify_format_policy(fullpath):
	if "mxf" in fullpath:
		policy = conf.video.master_format_policy
	elif "mp4" in fullpath:
		policy = conf.video.access_format_policy
	output = subprocess.check_output(["mediaconch","-p",policy,fullpath])
	if output.startswith("fail"):
		fro_bug = frameRate_Original_bug_check(output,fullpath)
		if fro_bug is True:
			return True
		else:
			print "failed master"
			print output
			policy = conf.video.ff_master_format_policy
			output = subprocess.check_output(["mediaconch","-p",policy,fullpath])
			if output.startswith("fail"):
				print "failed ff_master"
				#print output
				if "AudioCount" in output:
					print "needs new audio"
					return False
			else:
				return True
	else:
		return True
	
def separateLTOpacket(sfull,canonicalName,repo):
	endDirThousand = canonicalName.replace("v","")[:1]
	endDirThousand = endDirThousand + "000"
	dest = os.path.join(conf.video.repo,endDirThousand,s)
	foo = raw_input("eh")
	if not s.startswith("F") and not os.path.exists(dest):
		shutil.copytree(sfull,dest,ignore=shutil.ignore_patterns("*.mxf","*.mxf.md5"))
	subprocess.call([conf.python,os.path.join(os.pardir(conf.scriptRepo),"bagit","bagit.py"),'--md5',sfull])
	if not os.path.exists(os.path.join(dest,"baginfo")):
		os.makedirs(os.path.join(dest,"baginfo"))
	for f in os.listdir(sfull):
		if f.endswith(".txt"):
			shutil.copy2(os.path.join(sfull,f),os.path.join(dest,"baginfo"))

def send2repo(dn,newIngest,ltoStage,repo):
	print "foo"
						
def main():
	###INIT VARS###
	global conf
	conf = rawconfig.config()
	log.log("Started")
	parser = argparse.ArgumentParser(description="processes video transfers")
	parser.add_argument('-m',dest='m',choices=['batch','single'],default=False,help='mode, for processing a single transfer or a batch in new_ingest')
	parser.add_argument('-i','--input',dest='i',help="the rawcapture file.wav to process, single mode only")
	args = parser.parse_args()
	#newIngest = conf.video.new_ingest
	newIngest = "F:/"
	ltoStage = conf.video.lto_stage
	repo = conf.video.repo
	formatPolicy = conf.video.format_policy
	###END INIT###
	###WALK THRU NEW INGEST###
	if args.m is 'batch':
		for dirs,subdirs,files in os.walk(newIngest):
			for s in subdirs:
				print ""
				print s
				if s.startswith("$") or s.startswith("."):
					continue
				sfull = os.path.join(dirs,s)
				with ut.cd(sfull):
					###GET NAME OF ASSET###
					#can be cusb-v1234-pres or cusb-vm1234-pres or cusb-vm1234-5678-pres
					match = ''
					match = re.search(r"cusb-vm?" + s.replace("v","") + r"-(\d*-)?",os.listdir(os.getcwd())[0])
					if not match:
						print "Buddy, you need to check on " + s
						sys.exit()
					canonicalName = match.group()[:-1]
					###END GET NAME###
					#make sure our starting bits are correct, that we have hashes
					print canonicalName
					oc_upload_isgood = verify_opencube_upload(sfull,canonicalName)
					if not oc_upload_isgood:
						continue
					#make sidecar files for:
					#qctools report for the master
					#PBCore2 document
					make_sidecars(sfull,canonicalName)
					#verify format policy
					verifyFormatPolicy(sfull,canonicalName,formatPolicy)
					#verify quality of transfer
					#verifytransferqc()
				separateLTOpacket(sfull,canonicalName,repo)
				#send2repo(dn,newIngest,ltoStage,repo)
		###END WALK###
if __name__ == '__main__':
	main()