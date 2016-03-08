import hashlib
import os
import sys
import shutil


startObj = sys.argv[1] # grab argument from CL
startObj = startObj.replace("\\","/") # fun fact, windows lets you type both fwd and bck slashes in pathnames
dest = sys.argv[2]
dest = dest.replace("\\","/") # gotta have trailing slash here
if dest.endswith != "/": # check for said trailing slash
	dest = dest + "/"
endObj = dest + os.path.basename(startObj) # this is the file that we wanted to move, in its destination
soMD = startObj + ".md5"
eoMD = endObj + ".md5"
flist = [startObj, endObj]
blocksize = 65536 # reading a file in chunks this size more memory efficient
hasher = hashlib.md5() # specify method/ hashing algorithm
# soPath, soFname = os.path.split(startObj) placeholder

shutil.copy(startObj, dest) # actually copy the file from start to finish

#here's where the fun starts, generate checksums for both source and dest
for f in flist:
	fmd5 = f + ".md5" # concat with ext to make md5 file names
	with open(f, 'rb') as afile: # open da file
		buf = afile.read(blocksize) # read it into a buffer in block sized chunks
		while len(buf) > 0: # as long as there is something in the buffer
			hasher.update(buf) # append the buffer data to our hasher dict
			buf = afile.read(blocksize) # iterate
	with open(fmd5,"w") as text_file: # initialize a file that will contain the md5
		text_file.write(hasher.hexdigest() + " *" + startObj) # write it with the hash *filename
	print(hasher.hexdigest()) # print it to the screen too who cares

# open the hash files and compare their contents
with open(soMD,'r') as f1:
	with open(eoMD,'r') as f2:
		sf1 = f1.read()
		ef2 = f2.read()
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

	