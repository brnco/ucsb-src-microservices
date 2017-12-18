#!/usr/bin/env python
'''
rips an optical disc
'''
import os
import subprocess
import argparse
import re
import time
import sys
###UCSB modules###
import config as rawconfig
import util as ut
import logger as log
import mtd
import makestartobject as makeso

def go(cmdstr):
	'''
	runs a command, returns true if success, error is fail
	'''
	try:
		if os.name == 'posix':
			returncode = subprocess.check_output(cmdstr, shell=True)
		else:
			returncode = subprocess.check_output(cmdstr)
		return True
	except subprocess.CalledProcessError, e:
		returncode = e.returncode
		print returncode
		return returncode

def make_iso(args, file):
	'''
	makes the iso using ddrescue
	'''
	cmdstr = 'ddrescue -b 2048 -v ' + args.d + ' ' + file.isoFullPath + ' ' + file.logFullPath
	if not os.path.exists(file.dir):
		os.makedirs(file.dir)
	cmdWorked = go(cmdstr)
	if cmdWorked is not True:
		print 'rip-optical-disc encountered the following error while making the iso'
		print cmdWorked
		return False
	else:
		return True

def parse_input(args):
	file = ut.dotdict({})
	file.name = 'cusb-' + args.i
	file.ext = '.iso'
	file.dir = os.path.join(conf.video.new_ingest, args.i)
	file.isoFullPath = os.path.join(file.dir, file.name + file.ext)
	file.logFullPath = os.path.join(file.dir, file.name + '.log')
	file.broadcastFullPath = os.path.join(file.dir, file.name + "-broadcast." + "mov")
	file.accessFullPath = os.path.join(file.dir, file.name + "-acc." + conf.ffmpeg.vcodec_access_format)
	return file

def init_args():
	'''
	grip options from command line
	'''
	parser = argparse.ArgumentParser(description="rips an optical disc, DVD only, Mac OSX/ Linux only")
	parser.add_argument('-i', '--item', dest='i', help='the item/ accession number of the disc, with the a/v preceeding it, e.g. v1234')
	parser.add_argument('-d', '--drive', dest='d', default='/dev/disk3', help='the disc drive where the dvd is located, default is /dev/disk3. run "diskutil list" to locate')
	args = parser.parse_args()
	return args

def main():
	'''
	do the thing
	'''
	global conf
	conf = rawconfig.config()
	args = init_args()
	file = parse_input(args)
	processWorked = go('diskutil unmount ' + args.d)
	processWorked = make_iso(args, file)
	if processWorked is not True:
		print 'rip-optical-disc encountered an error'
		print 'see console output or log at:'
		print file.logFullPath
		print 'for more info'
		print 'exiting...'
	else:
		cmdstr = 'python ' + os.path.join(conf.scriptRepo, 'hashmove.py') + ' -nm ' + file.isoFullPath
		processWorked = go(cmdstr)
		cmdstr = 'diskutil eject ' + args.d
		processWorked = go(cmdstr)

if __name__ == '__main__':
	main()
