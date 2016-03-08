import hashlib
import os
import sys
import ntpath

startObj = sys.argv[1] # grab argument from CL
startObj = startObj.replace("\\","/") # fun fact, windows lets you type both fwd and bck slashes in pathnames
soPath, soFname = os.path.split(startObj) # placeholder
ofname = startObj + ".md5" # concat with ext to make output file name
BLOCKSIZE = 65536 # reading a file in chunks this size more memory efficient
hasher = hashlib.md5() # specify method/ hashing algorithm
with open(startObj, 'rb') as afile: # open da file
    buf = afile.read(BLOCKSIZE) # read it into a buffer in block sized chunks
    while len(buf) > 0: # as long as there is something in the buffer
        hasher.update(buf) # append the buffer data to our hasher dict
        buf = afile.read(BLOCKSIZE) # iterate
with open(ofname,"w") as text_file: # initialize a file that will contain the md5
	text_file.write(hasher.hexdigest() + " *" + startObj) # write it with the hash *filename
print(hasher.hexdigest()) # print it to the screen too who cares