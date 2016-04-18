#avlab-cylinders
#processes cylinders
#takes broadcast master, adds ID3 tags and 2s heads and tails fades (via makebroadcast.py)
#makes an mp3
#makes a SIP and movs to R:/Cylinders share (vis hashmove.py)

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
		for s in subdirs:
			with cd(os.path.join(captureDir, s)):
				print "Processing Cylinder" + s
				subprocess.call(['python','S:/avlab/microservices/makebroadcast.py',broadcastM,'-ff'])
				subprocess.call(['python','S:/avlab/microservices/makemp3.py','
	return

dependencies()
main()
