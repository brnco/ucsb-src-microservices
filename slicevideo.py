#!/usr/bin/env python
#splits a tape capture with n masters on it into individual files
#takes areguments for
#raw preservation capture file path
#master number, to triangulate the physical tape

import os
import subprocess
import sys
import glob
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

#check that we have the required software to run this script
def dependencies():
	depends = ['ffmpeg','ffprobe']
	for d in depends:
		if spawn.find_executable(d) is None:
			print "Buddy, you gotta install " + d
			sys.exit()
	return

def makenames(masterNum, vmNums): #does a bunch of string things to get us the right names for output files
	fPres= []
	fAcc = []
	for i, fname in enumerate(vmNums): #loop through the list of tuples
		vNum = fname.replace("m","") #drop the "m" for "video master", make it just a vNumber
		vNumPath = "R:/Visual/avlab/new_ingest/" + vNum + "/" #string a path that has this vNumber as its parent folder
		if not os.path.exists(vNumPath): #if that path doesn't exist yet, recursively make it
			os.makedirs(vNumPath)
		fPres.append(vNumPath + "cusb-" + fname + "-" + masterNum + "-pres.mxf") #make the new pres master name
		fAcc.append(vNumPath + "cusb-" + fname + "-" + masterNum + "-acc.mp4") #make the new access copy name
	return fPres, fAcc

def makeslices(fPres, fAcc, slicepoints, startPresObj, startAccObj):
	#build list of tuples here
	#[(vm0090, 4:08),(vm0091,6:00),...(vx1234,1:23)]
	#optional start time
	for i in range(1,len(slicepoints),1):
		presClip = [slicepoints[i-1],fPres[i-1],slicepoints[i]]
		accClip = [slicepoints[i-1],fAcc[i-1],slicepoints[i]]
		subprocess.call(['ffmpeg','-i',startPresObj,'-ss',slicepoints[i-1],'-c','copy','-t',slicepoints[i],fPres[i-1]])
		subprocess.call(['ffmpeg','-i',startAccObj,'-ss',slicepoints[i-1], '-c','copy','-t',slicepoints[i],fAcc[i-1]])
	return
	
dependencies()

startPresObj = sys.argv[1] #takes argument for raw pres capture
startPresObj = startPresObj.replace("\\","/")
startAccObj = startPresObj.replace("pres.mxf","acc.mp4")
masterKey = sys.argv[2] #physical tape number
vmNums = ['vm0092','vm0093','vm0094','vm0095','vm0096'] #list of visual masters on the tape
slicepoints = ['00:00:30.00','00:09:26.37','00:21:10.00','00:29:26.97','00:40:58.50','00:52:19.57'] #their in and out points
fPres, fAcc = makenames(masterKey, vmNums) #calls the makenames function
makeslices(fPres, fAcc, slicepoints, startPresObj, startAccObj) #calls the slicing function
