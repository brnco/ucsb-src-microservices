import hashlib
import os
import sys
import shutil


startObj = sys.argv[1] # grab argument from CL
startObj = startObj.replace("\\","/") # fun fact, windows lets you type both fwd and bck slashes in pathnames
dest = sys.argv[2]
dest = dest.replace("\\","/") # gotta have trailing slash here
if dest[-1] != "/": # check for said trailing slash
	dest = dest + "/"
if not os.path.exists(dest):
	os.makedirs(dest)
endObj = os.path.join(dest, os.path.basename(startObj)) # this is the file that we wanted to move, in its destination
soMD = startObj + ".md5"
eoMD = endObj + ".md5"
flist = [startObj, endObj]
# soPath, soFname = os.path.split(startObj) placeholder

shutil.copy2(startObj, dest) # actually copy the file from start to finish

#here's where the fun starts, generate checksums for both source and dest
def hashfile(afile, hasher, blocksize=65536):
	fmd5 = fname + ".md5" # concat with ext to make md5 file names
	buf = afile.read(blocksize) # read the file into a buffer cause it's more efficient for big files
	while len(buf) > 0: # little loop to keep reading
		hasher.update(buf) # here's where the hash is actually generated
		buf = afile.read(blocksize) # keep reading
	if not os.path.exists(fmd5): # if a sum already exists we don't wanna waste energy re-doing it. also a failsafe
		# THING: if a sum already exists in dest it wont be recalcd but idgaf
		with open(fmd5,"w") as text_file: # initialize a file that will contain the md5
			text_file.write(hasher.hexdigest() + " *" + fname) # write it with the hash *filename
	print hasher.hexdigest() # pop the results to the cli who cares
	return hasher.hexdigest() # close the file
	
[(fname, hashfile(open(fname, 'rb'), hashlib.md5())) for fname in flist] # call the function using files in the list

wait = raw_input("press any key to continue")

# open the hash files and compare their contents
with open(soMD,'r') as f1:
	with open(eoMD,'r') as f2:
		_sf1 = f1.read()
		sf1 = _sf1[0:32]
		_ef2 = f2.read()
		ef2 = _ef2[0:32]
		if sf1 == ef2:
			delyn = 1 # set an error level
		else:
			delyn = 0
			
# if the strings match it's ok to delete these start file and its hash	
if delyn == 1:
	f1.close()
	os.remove(startObj)
	os.remove(soMD)
else:
	print "uh there was an issue there"

	