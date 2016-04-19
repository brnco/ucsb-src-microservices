#avlab-cylinders
#processes cylinders
#takes broadcast master, adds ID3 tags and 2s heads and tails fades (via makebroadcast.py)
#makes an mp3
#makes a SIP and movs to R:/Cylinders share (via hashmove.py)

import os
import subprocess
import sys
import glob
import re
import argparse
from distutils import spawn

#Context manager for changing the current working directory
class cd:
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

#find if we have the required software to complete this script
def dependencies():
	depends = ['ffmpeg','ffprobe']
	for d in depends:
		if spawn.find_executable(d) is None:
			print "Buddy, you gotta install " + d
			sys.exit()
	return
	
def main():
	#initialize a capture directory
	captureDir = "R:/Cylinders/avlab/audio_captures/"
	#recursively walk through the capture directory, finding all files and 1 layer of subfolders
	for dirs, subdirs, files in os.walk(captureDir):
		for file in files:
			#get rid of the bs that wavelab creates
			if file.endswith(".gpk") or file.endswith(".bak") or file.endswith(".mrk"):
				os.remove(file)
		#for each folder in our capture directory
		for s in subdirs:
			#cd into it
			with cd(os.path.join(captureDir, s)):
				print "Processing Cylinder" + s
				#initialize
				startObj = 'cusb-cyl' + s + 'b.wav'
				interObj = 'cusb-cyl' + s + 'c.wav'
				if not os.path.exists(startObj): #if we don't have a b.wav file in the dir we should just stop
					print "Buddy, somethings not right here"
					sys.exit()
				else:
					subprocess.call(['python','S:/avlab/microservices/makebroadcast.py',startObj,'-ff']) #calls makebroadcast.py and tells it to insert 2s fades
					os.remove(startObj) #deletes the raw broadcast capture
					os.rename(interObj, startObj) #renames the itnermediate files as the broadcast master
					subprocess.call(['python','S:/avlab/microservices/makemp3.py',startObj]) #calls makemp3.py on the new broadcast master
			#opens a log and write "Cylinder12345" for each cylinder processed so we can change their catalog records later
			with open('R:/Cylinders/avlab/to-update.txt','a') as t:
				t.write("Cylinder" + s + "\n")
			#based on how we have our repo set up, find which set of 1000 files this cylinder belongs in
			endDirThousand = str(s)
			if len(endDirThousand) < 5:
				endDirThousand = endDirThousand[:1] + "000"
			else:
				endDirThousand = endDirThousand[:2] + "000"
			endDir = os.path.abspath(os.path.join("R:/Cylinders",endDirThousand,s)) #set a destination
			subprocess.call(['python','S:/avlab/microservices/hashmove.py',s,endDir]) #hashmove the file to its destination
	return

dependencies()
main()
