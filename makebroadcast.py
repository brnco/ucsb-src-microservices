import os
import subprocess
import sys
import glob

class cd:
    #Context manager for changing the current working directory
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

startObj = sys.argv[1]
vexts = ['.mxf','.mp4','.mkv']
aexts = ['.wav','.mp3']
def handling(theInput):
	ext = startObj[-4:]
	if not os.path.isfile(startObj):
		print "Buddy, that's not a file"
	if not ext in vexts and not ext in aexts:
		print "Buddy, that's not really a file we can deal with rn"
	else:
		if ext in vexts:
			print "itsa vid"
		if ext in aexts:
			print "itsa sound"
			useChar = startObj[-5:-4]
			ext = startObj[-4:]
			if useChar == 'a' or useChar == 'b' or useChar == 'c':
				print "ayyyyy there's a use char"
				fname = os.path.basename(os.path.abspath(startObj))
				fname = fname[:-5]
				print fname
			else:
				fname = os.path.basename(os.path.abspath(startObj))
				fname = fname[:-4]
				print fname
			
			#cool great
			#processingParameters based on use code, audio or video material
		#if no use code assume something
	return #processingParameters
handling(startObj)
#def audioProc(theInput):
	#find length
	#	subtract 2s
	#if not mtdInput
	#	gently suggest making one
	#ffmpeg theInput theMtdInput -c:a mp3 320k 44.1kHz afade id3 -output
	#return

#def videoProc(theInput):
	