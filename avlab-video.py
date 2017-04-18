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
import ConfigParser
import xml.etree.ElementTree as ET
from distutils import spawn

#Context manager for changing the current working directory
class cd:
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

#find if we have the correct software installed		
def dependencies():
	depends = ['ffmpeg','ffprobe','MediaInfo','python']
	for d in depends:
		if spawn.find_executable(d) is None:
			print "Buddy, you gotta install " + d
			sys.exit()

def makeSidecars(dn,newIngest):
	for dirs,subdirs,files in os.walk(newIngest):
		for f in files:
			if f.endswith(".mxf"):
				with cd(dirs):
					print os.getcwd()
					#instantiate var names of our output files
					_qctfile = f + '.qctools.xml.gz'
					_pbc2file = f + '.PBCore2.xml'
					_framemd5 = f + '.framemd5'
					#if there's not a qctools doc for it, make one
					if not os.path.exists(_qctfile):
						subprocess.call(['python','S:/avlab/microservices/makeqctoolsreport.py',f])
					#if there's not a PBCore2 doc for it, make one
					if not os.path.exists(_pbc2file):
						#gotta give the PBCore2 filename as concat string here, _pbc2file is a file object
						subprocess.call(['MediaInfo','--Output=PBCore2','--LogFile=' + _pbc2file,f])
					#if there's not a framemd5 for it, make one
					#if not os.path.exists(_framemd5):
						#gotta give the framemd5 filename as concat string here, _framemd5 is a file object
						#subprocess.call(['ffmpeg','-i',presfile,'-f','framemd5',presfile + '.framemd5'])

def verifyOpenCubeUpload(sfull,canonicalName):
	filetypes = ["-pres.mxf","-acc.mp4"]
	for f in filetypes:
		fullf = os.path.join(sfull,canonicalName + f)
		print fullf
		if not os.path.exists(fullf):
			print "Buddy, you need to check on " + s
			sys.exit()
		if not os.path.exists(fullf + ".md5"):
			print "make a hash for " + fullf

def verifyFormatPolicy(sfull,canonicalName,formatPolicy):
	fops = {}
	fips = {}
	ns = "{http://www.pbcore.org/PBCore/PBCoreNamespace.html}"
	fop = ET.parse(formatPolicy).getroot()
	fip = ET.parse(os.path.join(sfull,canonicalName + "-pres.mxf.PBCore2.xml")).getroot()
	for itrack in fop.findall(ns+'instantiationTracks'):
		fops['instantiation_tracks'] = itrack.text
	for ietrack in fop.findall(ns+'instantiationEssenceTrack'):
		if ietrack.find(ns+'essenceTrackType').text == "Video":
			fops['video_encoding'] = ietrack.find(ns+'essenceTrackEncoding').text
			fops['video_framerate'] = ietrack.find(ns+'essenceTrackFrameRate').text
			fops['video_bitdepth'] = ietrack.find(ns+'essenceTrackBitDepth').text
			fops['video_framesize'] = ietrack.find(ns+'essenceTrackFrameSize').text
		elif ietrack.find(ns+'essenceTrackType').text == "Audio":
			fops['audio_standard'] = ietrack.find(ns+'essenceTrackEncoding').text
			fops['audio_standard'] = ietrack.find(ns+'essenceTrackSamplingRate').text
			fops['audio_standard'] = ietrack.find(ns+'essenceTrackBitDepth').text
			for eta in ietrack.findall(ns+'essenceTrackAnnotation'):
				if eta.get('annotationType') == "Channel(s)":
					fops['audio_channels'] = eta.text
	for itrack in fip.findall(ns+'instantiationTracks'):
		fips['instantiation_tracks'] = itrack.text
	for ietrack in fip.findall(ns+'instantiationEssenceTrack'):
		if ietrack.find(ns+'essenceTrackType').text == "Video":
			fips['video_encoding'] = ietrack.find(ns+'essenceTrackEncoding').text
			fips['video_framerate'] = ietrack.find(ns+'essenceTrackFrameRate').text
			fips['video_bitdepth'] = ietrack.find(ns+'essenceTrackBitDepth').text
			fips['video_framesize'] = ietrack.find(ns+'essenceTrackFrameSize').text
		elif ietrack.find(ns+'essenceTrackType').text == "Audio":
			fips['audio_standard'] = ietrack.find(ns+'essenceTrackEncoding').text
			fips['audio_standard'] = ietrack.find(ns+'essenceTrackSamplingRate').text
			fips['audio_standard'] = ietrack.find(ns+'essenceTrackBitDepth').text
			for eta in ietrack.findall(ns+'essenceTrackAnnotation'):
				if eta.get('annotationType') == "Channel(s)":
					fips['audio_channels'] = eta.text
	for f in fops:
		print fops[f]
		print fips[f]
		if fops[f] != fips[f]:
			print canonicalName + " failed at " + f
	foo = raw_input("Eh")
	
def pre_verifyLTOpacket(sfull,canonicalName,ltoStage):
	sidecartypes = [".qctools.xml.gz",".PBCore2.xml"]
	for sct in sidecartypes:
		if not sct in str(os.listdir(sfull)):
			print "Buddy, you need to make a derivative " + sct + " for " + sfull
			#sys.exit()
				
def send2repo(dn,newIngest,ltoStage,repo):
	print "foo"
						
def main():
	config = ConfigParser.ConfigParser()
	dn, fn = os.path.split(os.path.abspath(__file__)) #grip the path to the directory where ~this~ script is located
	config.read(os.path.join(dn,"microservices-config.ini"))
	newIngest = config.get('video','new_ingest')
	ltoStage = config.get('video','lto_stage')
	repo = config.get('video','repo')
	formatPolicy = config.get('video','format_policy')
	for dirs,subdirs,files in os.walk(newIngest):
		for s in subdirs:
			print ""
			print s
			sfull = os.path.join(dirs,s)
			with cd(sfull):
				match = ''
				match = re.search(r"cusb-vm?" + s.replace("v","") + r"-(\d*-)?",os.listdir(os.getcwd())[0])
				if not match:
					print "Buddy, you need to check on " + s
					sys.exit()
				canonicalName = match.group()[:-1]
				print canonicalName
				#make sure our starting bits are correct, that we have hashes
				#verifyOpenCubeUpload(sfull,canonicalName)
				#make sidecar files for:
				#qctools report for the master
				#PBCore2 document
				#makeSidecars(dn,newIngest)
				#verify format policy
				verifyFormatPolicy(sfull,canonicalName,formatPolicy)
				#verify quality of transfer
				#verifytransferqc()
				#make sure we have everything we need to send it to LTO
				#pre_verifyLTOpacket(sfull,canonicalName,ltoStage)
				#send2repo(dn,newIngest,ltoStage,repo)

dependencies()
main()