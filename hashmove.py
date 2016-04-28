#better file movement
#takes arguments for source or dest, source can be file or dir, dest must be dir
#copies files, hashes pre and post copy, deletes if hashes match, deletes dir if empty

import hashlib
import os
import sys
import shutil
import time
import re
from optparse import OptionParser #OpenCube uses python 2.6 so has to be compatible, argparse not available until 2.7
import getpass

#figure out if arguments given are files or dirs, generate list of files and destinations to work on
def makelist(startObj,dest,flist=[],soisdir=''):
	if os.path.isfile(startObj):#if first argument is a file it's p easy
		soisdir = False
		endObj = os.path.join(dest, os.path.basename(startObj)) # this is the file that we wanted to move, in its destination
		flist = (startObj, endObj)
	#if the start object is a directory things get tricky
	elif os.path.isdir(startObj):
		soisdir = True #we'll use this later to delete these dirs
		if not startObj.endswith("/"):
			startObj = startObj + "/" #later, when we do some string subs, this keeps os.path.join() from breaking on a leading /
		for dirs, subdirs, files in os.walk(startObj): #walk recursively through the dirtree
			for x in files: #ok, for all files rooted at start object
				b = os.path.join(dirs,x) #make the full path to the file
				b = b.replace(startObj,'') #extract just path relative to startObj (the subdirtree that x is in)
				endObj = os.path.join(dest,b) #recombine the subdirtree with given destination
				_file = os.path.join(dirs, x) #if it's not, grab the start file full path
				filename, ext = os.path.splitext(_file) #separate extension from filename
				if not ext == '.md5': #check that the file found it not an md5 (no hashes of hashes here my friend)
					flist.extend((_file,endObj)) #add these items as a tuple to the list of files
	it = iter(flist) #i dunno but it's necessary
	flist = zip(it, it) #uhhhh, formally make that object into a list
	return flist, soisdir

#generate checksums for both source and dest
def hashfile(afile, hasher, blocksize=65536):
	fmd5 = afile.name + ".md5" # concat with ext to make md5 file names
	buf = afile.read(blocksize) # read the file into a buffer cause it's more efficient for big files
	while len(buf) > 0: # little loop to keep reading
		hasher.update(buf) # here's where the hash is actually generated
		buf = afile.read(blocksize) # keep reading
	if not os.path.exists(fmd5): # if a sum already exists we don't wanna waste energy re-doing it. also a failsafe
		# THING: if a sum already exists in dest it wont be recalcd but idgaf
		with open(fmd5,"w") as text_file: # initialize a file that will contain the md5
			text_file.write(hasher.hexdigest() + " *" + afile.name) # write it with the hash *filename
	#print hasher.hexdigest() # pop the results to the cli who cares
	return

#open the hash files and compare their contents
def compareDelete(bar):
	so, eo = bar #unpack tuples into startObject and endObject
	soMD = so + ".md5" #add md5 extensions
	eoMD = eo + ".md5"
	#open both md5 files
	with open(soMD,'r') as f1:
		with open(eoMD,'r') as f2:
			sf1 = re.search('\w{32}',f1.read()) #this searches for a 32char alphanumeric string (the md5 hash)
			ef2 = re.search('\w{32}',f2.read())
			print "srce " + os.path.basename(so) + " " + sf1.group().lower()
			print "dest " + os.path.basename(eo) + " " + ef2.group().lower()
			if sf1.group().lower() == ef2.group().lower(): #if they're the same that's great
				delyn = 1 # set an error level
			else: #fine too but it means the files aren't the same on both ends of transfer
				delyn = 0		
	if delyn == 1: #if the strings match it's ok to delete these start file and its hash	
		f1.close()
		os.remove(so)
		os.remove(soMD)
	else:
		print "uh there was an issue there"	
	return

def main():
	#initialize all of the things
	usage = "Usage: python %prog [-options] source destination"
	parser = OptionParser(usage=usage) #crate a parser object
	parser.add_option('-c','--copy',action='store_true',dest='c',default='None',help="copy, don't delete from source") #add an option to our parser object, in this case '-c' for copy
	parser.add_option('-l','--lto',action='store_true',dest='lto',default='None',help="write to lto, asks for lto barcode and logs files written")
	(options, args) = parser.parse_args() #parse the parser object, return list of options followed by positional parameters
	#args[] is the index of a positional argument, 0=source, 1=destination, in this case
	startObj = args[0].replace("\\","/") # fun fact, windows lets you type both fwd and back slashes in pathnames
	dest = args[1].replace("\\","/") # just easier to replace these slashes for windows sry
	if not os.path.exists(dest): # make the destination dir if it don't already exist
		os.makedirs(dest)
		
	#ok
	#return a list of tuples, files to move and their destinations
	flist, soisdir = makelist(startObj, dest)

	#copy each item from start to dest
	for f in flist:
		sf, ef = f #break list of tuples up into startfile and endfile
		print ""
		print "copying " + os.path.basename(sf) + " from source to destination..."
		if soisdir is False: #if the startObject is not a directory
			shutil.copy2(sf,ef) #if it's just a single file do a straight copy
		if soisdir is True: #if the startObject is a directory
			#make the subdirectories
			_dest = os.path.dirname(os.path.normpath(ef)) 
			if not os.path.exists(_dest):
				os.makedirs(_dest)
			shutil.copy2(sf,ef) #we use copy2 because it grabs all the registry metadata too
	
	#hash start and end files
	for sf, ef in flist:
		print ""
		print "hashing source and destination " + os.path.basename(sf)
		#to change the hashing algorithm just replace MD5 with SHA256 or whatever, remember to change extensions up top too!
		sf, hashfile(open(sf, 'rb'), hashlib.md5()), ef, hashfile(open(ef, 'rb'), hashlib.md5())
	
	
	if options.c is 'None': #if we are moving not copying, as declared by flag -c, delete the start object
		#compare and delete them
		for f in flist:
			print ""
			print "verifying source and destination hashes..."
			compareDelete(f)
			
		#if we hashmoved a dir, try to delete the now empty dir
		if soisdir is True:
			rmDirList = []
			for dirs, subdirs, files, in os.walk(startObj):
				for x in subdirs: #delete subdirs
					rmDirList.append(os.path.join(dirs,x))
					#os.rmdir(os.path.join(dirs,x))
			for rm in reversed(rmDirList):
				os.rmdir(rm)
				time.sleep(1.0) #gotta give the system time to catch up and recognize if a dir is empty
			os.rmdir(startObj)
	
	if options.lto is not 'None':
		ltoNumber = raw_input("What is the barcode of this LTO? ")
		usr = getpass.getuser()
		if usr == 'opencube':
			_ltoLog = "/DATA/special/DeptShare/special/avlab/lto-logs/" + ltoNumber + ".txt"
		else:
			_ltoLog = os.path.join(os.path.sep,'s','avlab','lto-logs',ltoNumber + ".txt")
		ltoLog = open(_ltoLog,"a")
		ltoLog.write(startObj + "\n")
		for sf, ef in flist:
			with open(ef + ".md5","r") as m:
				_emd5 = m.read()
				emd5 = _emd5[0:32]
				ltoLog.write(ef + " * " + emd5 + "\n")
		ltoLog.write("\n")
		ltoLog.close()
	return


main()
