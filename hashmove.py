import hashlib
import os
import sys
import ntpath
import shutil
import difflib


startObj = sys.argv[1] # grab argument from CL
startObj = startObj.replace("\\","/") # fun fact, windows lets you type both fwd and bck slashes in pathnames
dest = sys.argv[2]
dest = dest.replace("\\","/") # gotta have trailing slash here
endObj = dest + os.path.basename(startObj)
soMD = startObj + ".md5"
eoMD = endObj + ".md5"
shutil.copy(startObj, dest)
# soPath, soFname = os.path.split(startObj) placeholder
flist = [startObj, endObj]
blocksize = 65536 # reading a file in chunks this size more memory efficient
hasher = hashlib.md5() # specify method/ hashing algorithm

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


with open(soMD,'r') as f1:
	with open(eoMD,'r') as f2:
		sf1 = f1.read()
		ef2 = f2.read()
		if sf1 == ef2:
			delyn = 1
		else:
			delyn = 0
if delyn == 1:
	f1.close()
	os.remove(startObj)
	os.remove(soMD)
else:
	print "uh there was an issue there"
			