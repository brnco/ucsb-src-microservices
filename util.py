#!/usr/bin/env python
import os
import time
import unittest


def drivematch(path):
	if path.startswith("/") or path.startswith("\\"):
		path = path[1:]
	path.replace("\\","/")	
	if not os.name == 'posix': #if windows
		if "microservices-logs" in path:
			drive = "S:/"
		else:
			drive = "R:/"
		realpath = os.path.join(drive,path)
	else: #if mac/ unix
		if "microservices-logs" in path:
			drive = "/Volumes/special/DeptShare/special"
		elif "phi_raw-image-captures" in path:
			drive = desktop()
		else:
			drive = "/Volumes/special"
		realpath = os.path.join(drive,path)
	return realpath

def pythonpath():
	if os.name == 'posix':
		return "/usr/bin/python"
	else:
		return "C:/Python27/python.exe"
		
def desktop():
	try:
		desktop = os.path.join(os.environ["HOME"], "Desktop")
	except:
		desktop = os.path.join(os.environ["USERPROFILE"], "Desktop")
	return desktop

#Context manager for changing the current working directory
class cd:
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)
    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)
    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

#check that we have the required software to run a script
def dependencies(depends):
	for d in depends:
		if spawn.find_executable(d) is None:
			print "Buddy, you gotta install " + d
			sys.exit()
	return        

def rename_ucsb2cusb(path):
	path = path.replace("\\","/")
	if os.path.isfile(path):
		newname = path.replace("ucsb","cusb")
		os.rename(path,newname)
	else:
		for dirs, subdirs, files in os.walk(path):
			for f in files:
				if f.startswith("ucsb"):
					print f
					newname = f.replace("ucsb","cusb")
					print os.path.join(dirs,newname)
					os.rename(os.path.join(dirs,f),os.path.join(dirs,newname))
		time.sleep(3)
		for dirs, subdirs, files in os.walk(path):	
			for s in subdirs:
				if s.startswith("ucsb"):
					newname = s.replace("ucsb","cusb")
					os.rename(os.path.join(dirs,s),os.path.join(dirs,newname))
	return				

def make_end_use_char(start_use_char,filename):#makes the end use character for the output file
	#end use characters correspond to different parts of our OAIS implementation
	#filenames ending in "a" are our archival masters
	#filenames ending in "b" are our broadcast masters
	#filenames ending in "c" are intermediate files
	#filenames ending in "d" are access files
	if start_use_char == 'a':
		end_use_char = "b"
	elif start_use_char == 'm':
		end_use_char = ""
	elif start_use_char == 'b':
		end_use_char = 'c'
	elif start_use_char == 'c':
		end_use_char = "e"
	else:
		end_use_char = "b"
	return end_use_char
	
def make_asset_name(start_use_char, filename):
	if start_use_char:
		asset_name = filename[:-1]
	else:
		asset_name = filename
	return asset_name
	
	
#add /usr/local/bin prefix to python calls for macs		
class dotdict(dict):
	"""dot.notation access to dictionary attributes"""
	__getattr__ = dict.get
	__setattr__ = dict.__setitem__
	__delattr__ = dict.__delitem__


if __name__ == '__main__':
    unittest.main()