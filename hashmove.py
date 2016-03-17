#better file movement
#takes arguments for source or dest, source can be file or dir, dest must be dir
#copies files, hashes pre and post copy, deletes if hashes match, deletes dir if empty

import hashlib
import os
import sys
import shutil

#initialize a buncha stuff
startObj = sys.argv[1] # grab argument from CL
startObj = startObj.replace("\\","/") # fun fact, windows lets you type both fwd and back slashes in pathnames
dest = sys.argv[2]
dest = dest.replace("\\","/") # just easier to replace these slashes for windows sry
if not dest.endswith("/"):
	dest = dest + "/" #ADD TRAILING SLASH
if not os.path.exists(dest): # make the destination dir if it don't already exist
	os.makedirs(dest)

#figure out if arguments given are files or dirs, generate list of files to move
def makelist(startObj,dest,flist=[]):		
	if os.path.isfile(startObj):#if first argument is a file it's p easy
		soisdir = '0'
		endObj = os.path.join(dest, os.path.basename(startObj)) # this is the file that we wanted to move, in its destination
		flist = (startObj, endObj)
	if os.path.isdir(startObj):
		soisdir = '1'
		if not startObj.endswith("/"):
			startObj = startObj + "/" #add trailing slash
		for file in os.listdir(startObj):
			_file = os.path.join(startObj + str(file))
			filename, ext = os.path.splitext(_file)
			if not ext == '.md5':
				endObj = dest + os.path.basename(os.path.normpath(startObj)) + "/" + file
				print endObj
				flist.extend((_file,endObj))
	it = iter(flist)
	flist = zip(it, it)
	print flist
	return flist, soisdir
	blargh = raw_input("did that work y/n")
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
	print hasher.hexdigest() # pop the results to the cli who cares
	return

#open the hash files and compare their contents
def compareDelete(bar):
	so, eo = bar #unpack tuples into startObject and endObject
	soMD = so + ".md5" #add md5 extensions
	eoMD = eo + ".md5"
	#open both md5 files
	with open(soMD,'r') as f1:
		with open(eoMD,'r') as f2:
			_sf1 = f1.read()
			sf1 = _sf1[0:32] #read first 32 chars (length of md5 hash)
			_ef2 = f2.read()
			ef2 = _ef2[0:32]
			if sf1 == ef2: #if they're the same that's great
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

#ok make the list
flist, soisdir = makelist(startObj, dest)

#copy each item from start to end
for f in flist:
	sf, ef = f
	if soisdir == '0':
		shutil.copy2(sf,ef)
	if soisdir == '1':
		_dest = os.path.dirname(os.path.normpath(ef))
		if not os.path.exists(_dest):
			os.makedirs(_dest)
		shutil.copy2(sf,ef)

#hash start and end files
for sf, ef in flist:
	sf, hashfile(open(sf, 'rb'), hashlib.md5()), ef, hashfile(open(ef, 'rb'), hashlib.md5())

#compare and delete them
for f in flist:
	compareDelete(f)

#if we hashmoved a dir, try to delete the now empty dir
if soisdir == '1':
	os.rmdir(startObj)