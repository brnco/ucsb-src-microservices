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
import imp
import xml.etree.ElementTree as ET
from distutils import spawn


#find if we have the correct software installed		
def dependencies():
	depends = ['ffmpeg','ffprobe','MediaInfo','python']
	for d in depends:
		if spawn.find_executable(d) is None:
			print "Buddy, you gotta install " + d
			sys.exit()

def makeSidecars(sfull,canonicalName):
	#instantiate var names of our output files
	_qctfile = os.path.join(sfull,canonicalName + '.qctools.xml.gz')
	_pbc2file = os.path.join(sfull,canonicalName + '.PBCore2.xml')
	_framemd5 = os.path.join(sfull,canonicalName + '.framemd5')
	#if there's not a qctools doc for it, make one
	if not os.path.exists(_qctfile):
		subprocess.call(['python','S:/avlab/microservices/makeqctoolsreport.py',canonicalName + "-pres.mxf"])
	#if there's not a PBCore2 doc for it, make one
	if not os.path.exists(_pbc2file):
		#gotta give the PBCore2 filename as concat string here, _pbc2file is a file object
		subprocess.call(['MediaInfo','--Output=PBCore2','--LogFile=' + _pbc2file,canonicalName + "-pres.mxf"])
	#if there's not a framemd5 for it, make one
	#if not os.path.exists(_framemd5):
		#gotta give the framemd5 filename as concat string here, _framemd5 is a file object
		#subprocess.call(['ffmpeg','-i',presfile,'-f','framemd5',presfile + '.framemd5'])

#checks that uploads from the opencube are complete and good
def verifyOpenCubeUpload(sfull,canonicalName):
	filetypes = ["-pres.mxf","-acc.mp4"] #required filetypes
	for f in filetypes:
		fullf = os.path.join(sfull,canonicalName + f)
		print fullf
		if not os.path.exists(fullf):
			print "Buddy, you need to check on " + s
			sys.exit()
		if not os.path.exists(fullf + ".md5"):
			print "make a hash for " + fullf

#verifies that the uploads from opencube are well-formed and meet our format expectations
def verifyFormatPolicy(sfull,canonicalName,formatPolicy):
	fops = {} #format policy
	fips = {} #file policy
	ns = "{http://www.pbcore.org/PBCore/PBCoreNamespace.html}" #placeholder for namespace string, could be implemented as dict
	fop = ET.parse(formatPolicy).getroot() #get xml root from formatPolicy xml doc
	fip = ET.parse(os.path.join(sfull,canonicalName + "-pres.mxf.PBCore2.xml")).getroot() #get policy of file at hand
	#fill dictionary with policy specs
	for itrack in fop.findall(ns+'instantiationTracks'):
		fops['instantiation_tracks'] = itrack.text
	for ietrack in fop.findall(ns+'instantiationEssenceTrack'):
		if ietrack.find(ns+'essenceTrackType').text == "Video":
			fops['video_encoding'] = ietrack.find(ns+'essenceTrackEncoding').text
			fops['video_framerate'] = ietrack.find(ns+'essenceTrackFrameRate').text
			fops['video_bitdepth'] = ietrack.find(ns+'essenceTrackBitDepth').text
			fops['video_framesize'] = ietrack.find(ns+'essenceTrackFrameSize').text
		elif ietrack.find(ns+'essenceTrackType').text == "Audio":
			fops['audio_encoding'] = ietrack.find(ns+'essenceTrackEncoding').text
			fops['audio_samplingrate'] = ietrack.find(ns+'essenceTrackSamplingRate').text
			fops['audio_bitdepth'] = ietrack.find(ns+'essenceTrackBitDepth').text
			for eta in ietrack.findall(ns+'essenceTrackAnnotation'):
				if eta.get('annotationType') == "Channel(s)":
					fops['audio_channels'] = eta.text
	#fill dicitonary with file specs
	for itrack in fip.findall(ns+'instantiationTracks'):
		fips['instantiation_tracks'] = itrack.text
	for ietrack in fip.findall(ns+'instantiationEssenceTrack'):
		if ietrack.find(ns+'essenceTrackType').text == "Video":
			fips['video_encoding'] = ietrack.find(ns+'essenceTrackEncoding').text
			fips['video_framerate'] = ietrack.find(ns+'essenceTrackFrameRate').text
			fips['video_bitdepth'] = ietrack.find(ns+'essenceTrackBitDepth').text
			fips['video_framesize'] = ietrack.find(ns+'essenceTrackFrameSize').text
		elif ietrack.find(ns+'essenceTrackType').text == "Audio":
			fips['audio_encoding'] = ietrack.find(ns+'essenceTrackEncoding').text
			fips['audio_samplingrate'] = ietrack.find(ns+'essenceTrackSamplingRate').text
			fips['audio_bitdepth'] = ietrack.find(ns+'essenceTrackBitDepth').text
			for eta in ietrack.findall(ns+'essenceTrackAnnotation'):
				if eta.get('annotationType') == "Channel(s)":
					fips['audio_channels'] = eta.text
	#compare the two
	for f in fops:
		print fops[f]
		print fips[f]
		if fops[f] != fips[f]:
			print canonicalName + " failed at " + f
			foo = raw_input("Eh")
	
def separateLTOpacket(sfull,canonicalName,ltoStage):
	endDirThousand = canonicalName.replace("v","")[:1]
	endDirThousand = endDirThousand + "000"
	dest = os.path.join(repo,endDirThousand,s)
	if not s.startswith("F") and not os.path.exists(dest):
		shutil.copytree(sfull,dest,ignore=shutil.ignore_patterns("*.mxf","*.mxf.md5"))
	subprocess.call(["python",os.path.join(os.pardir(conf.scriptRepo),"bagit","bagit.py"),'--md5',sfull])
	if not os.path.exists(os.path.join(dest,"baginfo")):
		os.makedirs(os.path.join(dest,"baginfo"))
	for f in os.listdir(sfull):
		if f.endswith(".txt"):
			shutil.copy2(os.path.join(sfull,f),os.path.join(dest,"baginfo"))

def send2repo(dn,newIngest,ltoStage,repo):
	print "foo"
						
def main():
	###INIT VARS###
	dn, fn = os.path.split(os.path.abspath(__file__))
	global conf
	rawconfig = imp.load_source('config',os.path.join(dn,'config.py'))
	conf = rawconfig.config()
	global ut
	ut = imp.load_source("util",os.path.join(dn,"util.py"))
	global log
	log = imp.load_source('log',os.path.join(dn,'logger.py'))
	log.log("Started")
	newIngest = conf.video.new_ingest
	ltoStage = conf.video.lto_stage
	repo = conf.video.repo
	formatPolicy = conf.video.format_policy
	###END INIT###
	###WALK THRU NEW INGEST###
	for dirs,subdirs,files in os.walk(newIngest):
		for s in subdirs:
			print ""
			print s
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
				print canonicalName
				#make sure our starting bits are correct, that we have hashes
				verifyOpenCubeUpload(sfull,canonicalName)
				#make sidecar files for:
				#qctools report for the master
				#PBCore2 document
				makeSidecars(dn,newIngest)
				#verify format policy
				verifyFormatPolicy(sfull,canonicalName,formatPolicy)
				#verify quality of transfer
				#verifytransferqc()
			separateLTOpacket(sfull,canonicalName,repo,ltoStage)
			#send2repo(dn,newIngest,ltoStage,repo)
	###END WALK###
dependencies()
main()