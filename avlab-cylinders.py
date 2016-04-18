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

class cd:
    #Context manager for changing the current working directory
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

def dependencies():
	depends = ['ffmpeg','ffprobe']
	for d in depends:
		if spawn.find_executable(d) is None:
			print "Buddy, you gotta install " + d
			sys.exit()
	return
	
def main():
	captureDir = "R:/Cylinders/avlab/audio_captures/"
	for dirs, subdirs, files in os.walk(captureDir):
		for file in files:
			if file.endswith(".gpk") or file.endswith(".bak") or file.endswith(".mrk"):
				os.remove(file)
		for s in subdirs:
			with cd(os.path.join(captureDir, s)):
				print "Processing Cylinder" + s
				startObj = 'cusb-cyl' + s + 'b.wav'
				interObj = 'cusb-cyl' + s + 'c.wav'
				if not os.path.exists(startObj):
					print "Buddy, somethings not right here"
				else:
					subprocess.call(['python','S:/avlab/microservices/makebroadcast.py',startObj,'-ff'])
					os.remove(startObj)
					os.rename(interObj, startObj)
					subprocess.call(['python','S:/avlab/microservices/makemp3.py',startObj])
			with open('R:/Cylinders/avlab/to-update.txt','a') as t:
				t.write("Cylinder" + s + "\n")
			endDirThousand = str(s)
			if len(endDirThousand) < 5:
				endDirThousand = endDirThousand[:1] + "000"
			else:
				endDirThousand = endDirThousand[:2] + "000"
			endDir = os.path.join("R:/Cylinders",endDirThousand,s)
			print os.getcwd()
			subprocess.call(['python','S:/avlab/microservices/hashmove.py',s,endDir])
	return

dependencies()
main()
