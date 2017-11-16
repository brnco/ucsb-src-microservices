#! /usr/bin/env python
'''
nj_pre-SIP
verifies that all relevant filetypes exist (and, one day, conform) to NJ SIP
'''
import getpass
import os
import subprocess
import argparse
import re
###UCSB modules###
import config as rawconfig
import util as ut
import logger as log
import mtd
import makestartobject as makeso

def verify_package_contents(**kwargs):
	'''
	checks that every file type is in the SIPable dir
	'''
	args = ut.dotdict(kwargs)
	packageIsComplete = {}
	for filetype in args.filetypes:
		packageIsComplete[filetype]=False
		for file in os.listdir(args.fullpath):
			if file.endswith(filetype):
				packageIsComplete[filetype]=True
				continue
	for pic,v in packageIsComplete.iteritems():
		if v is False:
			return False
	return True

def move_package_toRepo(**kwargs):
	'''
	use hashmove to move the dir to the batch dir
	'''
	args = ut.dotdict(kwargs)
	output = subprocess.Popen(['python',os.path.join(args.scriptRepo,'hashmove.py'),args.fullpath,os.path.join(args.repo,args.assetName)],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	foo,err = output.communicate()
	if err:
		print err
		return False
	else:
		print foo
		sourcehash = re.search('srce\s\S+\s\w{32}',foo)
		desthash = re.search('dest\s\S+\s\w{32}',foo)
		dh = desthash.group()
		sh = sourcehash.group()
		if sh[-32:].lower() == dh[-32:].lower():
			return True
		else:
			return False

def make_assetName_fullpath(startObj):
	'''
	returns the canonical assetName and fullpath to SIPable directory
	'''
	#if not (startObj.startswith("R:/") or startObj.startswith("//svmwindows")) and not os.path.isdir(startObj):
	if not os.path.isdir(startObj):
		sobj = makeso.parse_input(startObj)
		assetName = os.path.basename(os.path.dirname(sobj))
		fullpath = sobj.replace(os.path.basename(sobj),"")[:-1]
	else:
		assetName = os.path.basename(os.path.normpath(startObj))
		fullpath = startObj
	return assetName, fullpath

def main():
	'''
	do the thing
	'''
	###INIT VARS###
	log.log("started")
	global conf
	conf = rawconfig.config()
	parser = argparse.ArgumentParser(description="makes a SIP")
	parser.add_argument('-i','--input',dest='i',help="the directory or asset name which you would like to SIP")
	parser.add_argument('-m','--mode',dest='m',choices=['nj'],help="mode, the type of SIP to make")
	args = parser.parse_args()
	###END INIT###
	if args.m == 'nj':
		###init kwargs objects###
		kwargs = {"materialType":"nj","new_ingest":conf.NationalJukebox.PreIngestQCDir,"repo":conf.NationalJukebox.BatchDir,"scriptRepo":conf.scriptRepo}
		kwargs['filetypes'] = ['m.wav','.wav','.tif','.cr2','.jpg']
		kwargs['assetName'], kwargs['fullpath'] = make_assetName_fullpath(args.i)
		###end init###
		packageIsComplete = verify_package_contents(**kwargs)
		if packageIsComplete:
			moveSuccess = move_package_toRepo(**kwargs)
			if moveSuccess:
				print "yeah"
			else:
				print "There was a problem moving the SIP to the repo"
		else:
			print "The supplied package is not complete, no SIP made"

if __name__ == '__main__':
	main()
	log.log("complete")
