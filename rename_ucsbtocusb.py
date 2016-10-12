#!/usr/bin/env python
#rename_ucsbtocusb
#takes the input string for directory path with files/ subdirs named "ucsb" and converts them to "cusb"
#legacy programming error causes barcodes and filenames to print with ucsb so this script fixes it in post

import os
import sys
import time
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

def dofiles(where):
	for dirs, subdirs, files in os.walk(where):
		for f in files:
			if f.startswith("ucsb"):
				with cd(dirs):
					os.rename(f, 'cusb' + f[4:]) #stronger ways to do this
	return

def dodirs(where):
	for dirs, subdirs, files in os.walk(where):
		for s in subdirs:
				if s.startswith("ucsb"):
					with cd(dirs):
						os.rename(s, 'cusb' + s[4:])
	return
	
def main():
	parser = argparse.ArgumentParser(description="renames everything in [path] from ucsb to cusb")
	parser.add_argument('where',help='the path to rename')
	args = vars(parser.parse_args()) #create a dictionary instead of leaving args in NAMESPACE land
	where = args['where'].replace("\\","/") #for the windows peeps
	dofiles(where) #does it for files
	time.sleep(3) #give the os time to recooperate
	dodirs(where) #does it for dirs
	return

main()
