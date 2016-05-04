#better file movement
#takes arguments for source or dest, source can be file or dir, dest must be dir
#copies files, hashes pre and post copy, deletes if hashes match, deletes dir if empty

import hashlib
import os
import sys
import shutil
import time
import re
import argparse
import getpass

#generate lists of pairs of start and end files
def makeflist(startObj,dest,startObjIsDir,hashalg,flist=[]):
	if startObjIsDir is False: #if first argument is a file it's p easy
		endObj = os.path.join(dest, os.path.basename(startObj)) # this is the file that we wanted to move, in its destination
		flist = (startObj, endObj)
	#if the start object is a directory things get tricky
	else:
		if not startObj.endswith("/"):
			startObj = startObj + "/" #later, when we do some string subs, this keeps os.path.join() from breaking on a leading / I HATE HAVING TO DO THIS
		for dirs, subdirs, files in os.walk(startObj): #walk recursively through the dirtree
			for x in files: #ok, for all files rooted at start object
				b = os.path.join(dirs,x) #make the full path to the file
				b = b.replace(startObj,'') #extract just path relative to startObj (the subdirtree that x is in)
				endObj = os.path.join(dest,b) #recombine the subdirtree with given destination (and file.extension)
				startFile = os.path.join(dirs, x) #grab the start file full path
				startFilename, ext = os.path.splitext(startFile) #separate extension from filename
				if not ext == '.' + hashalg: #check that the file found doesn't have the hash extension (no hashes of hashes here my friend)
					flist.extend((startFile,endObj)) #add these items as a tuple to the list of files
	it = iter(flist) #i dunno but it's necessary
	flist = zip(it, it) #uhhhh, formally make that object into a list
	return flist

def makehlist(aflist,hashalg,grip):
	hd = {} #if you declare this a default in the function def you'll get a memory error :/
	for af in aflist:
		afhashfile = af + "." + hashalg #make a name for the start file's hash file
		if grip is True and os.path.isfile(afhashfile): #check to see if it exists (so we don't recalc)
			with open(afhashfile,'r') as f: #open it
				afhash = re.search('\w{32}',f.read()) #find an alphanumeric string that's 32 chars long (works for md5)
			hd[os.path.basename(af)] = afhash.group() #append the key : value pairs to the start hash dictionary
		else:
			hd[os.path.basename(af)] = hashfile(open(af, 'rb'), hashalg)
	return hd

#generate checksums for both source and dest
def hashfile(afile, hashalg, blocksize=65536):
	hasher = hashlib.new(hashalg) #grab the hashing algorithm decalred by user
	buf = afile.read(blocksize) # read the file into a buffer cause it's more efficient for big files
	while len(buf) > 0: # little loop to keep reading
		hasher.update(buf) # here's where the hash is actually generated
		buf = afile.read(blocksize) # keep reading
	return hasher.hexdigest()

def printhashes(sflist,shd,eflist,ehd,hashalg):
	for sf in sflist: #loop thru list of start files
			for sh in shd: #for each start hash
				sfhfile = sf + "." + hashalg #make the filename for the sidecar file
				if not os.path.isfile(sfhfile): #if it doesn't already exist
					txt = open(sfhfile, "w") #old school
					txt.write(shd[sh] + " *" + sh) #lmao at these var names, writes [the start hash from the start hash dict *the filename]
					txt.close()
	for ef in eflist: #repeat for endfiles
		for eh in ehd:
			efhfile = ef + "." + hashalg
			if not os.path.isfile(efhfile):
				txt = open(efhfile, "w")
				txt.write(ehd[eh] + " *" + eh)
				txt.close() 
	return
	
def main():
	#initialize arguments coming in from cli
	parser = argparse.ArgumentParser()
	parser.add_argument('-c','--copy',action='store_true',dest='c',default=False,help="copy, don't delete from source")
	parser.add_argument('-l','--log',action='store_true',dest='l',default=False,help="write to log in cwd (editable)")
	parser.add_argument('-q','--quiet',action='store_true',dest='q',default=False,help="quiet mode, don't print anything to console")
	parser.add_argument('-v','--verify',action='store_true',dest='v',default=False,help="verify mode, verifies sidecar hash(es) for file or dir")
	parser.add_argument('-a','--algorithm',action='store',dest='a',default='md5',choices=['md5','sha1','sha256','sha512'],help="the hashing algorithm to use")
	parser.add_argument('-np','--noprint',action='store_true',dest='np',default=False,help="no print mode, don't generate sidecar hash files")
	parser.add_argument('startObj',help="the file or directory to hash/ move/ copy/ verify/ delete")
	parser.add_argument('endObj',nargs='?',default=os.getcwd(),help="the destination parent directory")
	args = parser.parse_args()
	
	#housekeeping
	startObj = args.startObj.replace("\\","/") #everything is gonna break if we don't do this for windows ppl
	if args.v is True and args.endObj == os.getcwd(): #if we're verifying a directory against itself, not another directory
		endObj = args.startObj.replace("\\","/")
		grip = False #determines if we grip the hash value from a previously existing sidecar file
	else:
		endObj = args.endObj.replace("\\","/")
		grip = True
	if args.q is True: #quiet mode redirects standard out to nul
		f = open(os.devnull,'w')
		sys.stdout = f
	hashAlgorithm = hashlib.new(args.a) #creates a hashlib object that is the algorithm we're using
	if os.path.isdir(startObj): #flag if the start object is a directory or not
		startObjIsDir = True
	elif os.path.isfile(startObj):
		startObjIsDir = False
	else: #if something is up we gotta exit
		print "Buddy, something isn't right here..."
		sys.exit()
		
	#make lists of files
	flist = makeflist(startObj, endObj, startObjIsDir, args.a)
	sflist = [x for x,_ in flist]
	eflist = [x for _,x in flist]

	#placeholder: copy files goes here
	
	#make dicts of filenames : hashes
	shd = makehlist(sflist, args.a, True)
	ehd = makehlist(eflist, args.a, grip)
	
	#print the hashes
	if args.np is False:
		printhashes(sflist,shd,eflist,ehd,args.a)
		
	#compare the dict values and provide feedback
	
	#based on feedback, remove start objects
	
	#print log to cwd of what happened
	return
	

main()