#!/usr/bin/env python
#hashmove.py
#better file movement
#takes arguments for source or dest, source can be file or dir, dest must be dir
#copies files, hashes pre and post copy, deletes if hashes match, deletes dir if empty
#you can also:
#verify against another directory or the given directory (-v)
#copy files, don't delete from source directory (-c)
#quiet mode (-q)
#don't print sidecar files (-np)
#print logs to current directory (-l)

#######################################################################################################################
#here's a list of the lists used in this script because there's a lot
#flist = file list. composed of string tuples of start and end file paths
#sflist = start file list. strings of start file paths
#eflist = end file list. strings of end file paths
#sfhflist = start file hash file list. strings of the full paths of the sidecar hash files for source files
#efhflist = end file hash file list. strings of the full paths of the sidecar hash files for destination
#matches = list of filepaths whose hashes match, either after copy or after recalc (in the case of verifying)
#mismatches = list of filepaths whose hashes don't match, either after copy or after recalc (in the case of verifying)
#shd = start hash dictionary. filename.ext : hash-value pairs for start files
#ehd = end hash dictionary. filename.ext : hash-value pairs for end files
#######################################################################################################################


import hashlib
import os
import sys
import shutil
import time
import re
import argparse
import getpass
import subprocess

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

def makehlist(aflist,hashalg,hashlength,grip):
	hd = {} #if you declare this a default in the function def you'll get a memory error :/
	for af in aflist:
		afhashfile = af + "." + hashalg #make a name for the start file's hash file
		if grip is True and os.path.isfile(afhashfile): #check to see if it exists (so we don't recalc)
			with open(afhashfile,'r') as f: #open it
				afhash = re.search('\w{'+hashlength+'}',f.read()) #find an alphanumeric string that's 32 chars long (works for md5)
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
	sfhflist = []
	for sf in sflist: #loop thru list of start files
		sfhfile = sf + "." + hashalg #make the filename for the sidecar file
		sfhflist.extend([sfhfile])
		if os.path.exists(sfhfile):
			os.remove(sfhfile)
		txt = open(sfhfile, "w") #old school
		txt.write(shd[os.path.basename(sf)] + " *" + os.path.basename(sf)) #lmao at these var names, writes [the start hash from the start hash dict *the filename]
		txt.close()
	for ef in eflist: #repeat for endfiles
		efhfile = ef + "." + hashalg
		if os.path.exists(efhfile):
			os.remove(efhfile)
		txt = open(efhfile, "w")
		txt.write(ehd[os.path.basename(ef)] + " *" + os.path.basename(ef))
		txt.close() 
	return sfhflist
	
def copyfiles(flist):
	win=mac=False
	if sys.platform.startswith("darwin"):
		mac=True
	elif sys.platform.startswith("win"):
		win=True
	cmd=None

	for sf,ef in flist:
		print ""
		print "copying " + os.path.basename(sf) + " from source to destination..."
		_dest = os.path.dirname(os.path.normpath(ef)) 
		if not os.path.exists(_dest):
			os.makedirs(_dest)
		if mac:
			cmd=['cp',sf,ef]
		elif win:
			srce = os.path.dirname(sf)
			dest = os.path.dirname(ef)
			name,ext = os.path.split(sf)
			cmd=['robocopy',srce,dest,ext]
			print cmd
		subprocess.call(cmd)
	return
	
def deletefiles(sflist,sfhflist,startObj,matches,startObjIsDir):
	#initialize some lists
	delfiles = []
	delhfiles = []
	deldirs = []
	for match in matches:
		delfiles.extend([s for s in sflist if match in s])
		#^^^what this means is:
		#for each full path (s) in the start file list (sflist)
		#if the filename (match) is in full path (s)
		#extend the list delfiles
		delhfiles.extend([a for a in sfhflist if match in a])
		#print delfiles
	delfiles = list(set(delfiles)) #de-dupe
	delhfiles = list(set(delhfiles)) #de-dupe
	if startObjIsDir is True:
		deldirs.append(startObj)	#controls for empty top-dirs
		for d in delfiles:			#loop through file's we're going to delete and grip their containing folders
			deldirs.append(os.path.dirname(d))
	deldirs = list(set(deldirs)) #de-dupe
	for rmf in delfiles:
		#print rmf
		#print id(rmf)
		time.sleep(1.0)
		os.remove(rmf)
	for rmh in delhfiles:
		#print rmh
		time.sleep(1.0)
		os.remove(rmh)
	for rmd in reversed(sorted(deldirs, key=len)):
		time.sleep(1.0)
		os.rmdir(rmd)	
	return
	
def compare(shd, ehd):
	matches = []
	mismatches = []
	for skey in shd:
		print "srce " + skey + " " + shd[skey]
		print "dest " + skey + " " + ehd[skey]
		if not shd[skey].lower() == ehd[skey].lower():
			mismatches.extend([skey])
		else:
			matches.extend([skey])
	return matches, mismatches

def log(matches,mismatches,ehd):
	txtFile = open("log_" + time.strftime("%Y-%m-%d_%H%M%S") + ".txt", "w") #name log file log_YYYY-MM-DD_HourMinSec.txt
	txtFile.write("The following were successful:\n")
	for match in matches:
		if match in ehd:
			txtFile.write(match + " : " + ehd[match] + "\n")
	txtFile.write("The following were unsuccessful:")
	for mis in mismatches:
		if mis in ehd:
			txtfile.write(mis + " : " + ehd[mis] + "\n")
	txtFile.close()
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
	parser.add_argument('-nm','--nomove',action='store_true',dest='nm',default=False,help="no move mode, hash the file in place only")
	parser.add_argument('-g','--grip',action='store_true',dest='g',default=False,help="use hash values from existing sidecar files, default is False")
	parser.add_argument('startObj',help="the file or directory to hash/ move/ copy/ verify/ delete")
	parser.add_argument('endObj',nargs='?',default=os.getcwd(),help="the destination parent directory")
	args = parser.parse_args()
	###INIT VARS###
	flist = []
	sflist = []
	eflist = []
	ehd = []
	shd = []
	matches = []
	mismatches = []
	###END INIT###
	
	#housekeeping
	startObj = args.startObj.replace("\\","/") #everything is gonna break if we don't do this for windows ppl
	if args.v is True and args.endObj == os.getcwd(): #if we're verifying a directory against itself, not another directory
		endObj = args.startObj.replace("\\","/")
	else:
		endObj = args.endObj.replace("\\","/")
	if args.q is True: #quiet mode redirects standard out to nul
		f = open(os.devnull,'w')
		sys.stdout = f
	grip = args.g
	hashAlgorithm = hashlib.new(args.a) #creates a hashlib object that is the algorithm we're using
	hashlengths = {'md5':'32','sha1':'40','sha256':'64','sha512':'128'}
	hashlength = hashlengths[args.a] #set value for comparison later
	if os.path.isdir(startObj): #flag if the start object is a directory or not
		startObjIsDir = True
	elif os.path.isfile(startObj):
		startObjIsDir = False
	else: #if something is up we gotta exit
		print "Buddy, something isn't right here..."
		sys.exit()
		
	#make lists of files
	flist = makeflist(startObj, endObj, startObjIsDir, args.a)
	sflist = [x for x,_ in flist] #make list of startfiles
	if args.nm is False:
		eflist = [x for _,x in flist] #make list of endfiles

	#copy files from source to destination
	if args.v is False and args.nm is False:
		copyfiles(flist)
	
	#make dicts of filenames : hashes
	if args.nm is False:
		ehd = makehlist(eflist, args.a, hashlength, grip) #end hash dictionary
	shd = makehlist(sflist, args.a, hashlength, True) #start hash dictionary
	
	#print the hashes
	if args.np is False:
		sfhflist = printhashes(sflist,shd,eflist,ehd,args.a)
	
	#compare the dict values and provide feedback
	if args.nm is False:
		matches, mismatches = compare(shd, ehd)
	elif args.nm is True:
		for skey in shd:
			print "srce " + skey + " " + shd[skey]
	for m in mismatches:
		print "The following file hash did not match: " + m
	
	#based on feedback, remove start objects
	if args.c is False and args.v is False:
		deletefiles(sflist,sfhflist,startObj,matches,startObjIsDir)
		
	#print log to cwd of what happened
	if args.l is True:
		log(matches,mismatches,ehd)

main()
