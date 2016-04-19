#rename_ucsbtocusb
#takes the input string "ucsb" and converts it to "cusb"
#for both files and folders
#legacy programming error causes barcodes and filenames to print with ucsb so this script fixes it in post

import os
import sys
import fnmatch
import time

#Context manager for changing the current working directory
class cd:
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

def findfiles(pattern, path):
	filelist = []
	dirlist = []
	for root, dirs, files in os.walk(path): #recursively walk thru the dirtree
		for fname in files: #for each file found
			if fnmatch.fnmatch(fname, pattern): #if the filename contains the string in "pattern" (which is 'ucsb')
				with cd(root): #cd into the dir
					os.rename(fname,'cusb' + fname[4:])	#rename it with the new string in the first four chars		

	return

def finddirs(pattern, path):
	for root, dirs, files in os.walk(path):
		for dname in dirs:
			if fnmatch.fnmatch(dname, pattern):
				with cd(root):
					os.rename(dname,'cusb' + dname[4:])
	return

where = sys.argv[1]
where = where.replace("\\","/") #for the windows peeps
if not where.endswith("/"): #this is old
	where = where + "/" #ugh
findfiles('ucsb*', where) #does it for files
time.sleep(5) #give the os time to recooperate
finddirs('ucsb*', where) #calls the function