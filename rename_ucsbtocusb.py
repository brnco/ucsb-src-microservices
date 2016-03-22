import os
import sys
import fnmatch
import time
class cd:
    #Context manager for changing the current working directory
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
	for root, dirs, files in os.walk(path):
		for fname in files:
			if fnmatch.fnmatch(fname, pattern):
				with cd(root):
					os.rename(fname,'cusb' + fname[4:])			

	return
def finddirs(pattern, path):
	for root, dirs, files in os.walk(path):
		for dname in dirs:
			if fnmatch.fnmatch(dname, pattern):
				with cd(root):
					os.rename(dname,'cusb' + dname[4:])
	return

where = sys.argv[1]
where = where.replace("\\","/") # just easier to replace these slashes for windows sry
if not where.endswith("/"):
	where = where + "/"
findfiles('ucsb*', where)
time.sleep(5)
finddirs('ucsb*', where)