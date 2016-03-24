#splits a tape capture with n masters on it into individual files
#takes areguments for
#archival master
#master number

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

def makenames(masterNum, vmNums):
	fPres= []
	fAcc = []
	for i, fname in enumerate(vmNums):
		vNum = fname.replace("m","")
		vNumPath = "R:/Visual/avlab/new_ingest/" + vNum + "/"
		if not os.path.exists(vNumPath):
			os.makedirs(vNumPath)
		fPres.append(vNumPath + "cusb-" + fname + "-" + masterNum + "-pres.mxf")
		fAcc.append(vNumPath + "cusb-" + fname + "-" + masterNum + "-acc.mp4")
	print fPres
	print fAcc
	return fPres, fAcc

def makeslices(fPres, fAcc, slicepoints, startPresObj, startAccObj):
	#build list of tuples here
	#[(vm0090, 4:08),(vm0091,6:00),...(vx1234,1:23)]
	#optional start time
	for i in range(1,len(slicepoints),1):
		presClip = [slicepoints[i-1],fPres[i-1],slicepoints[i]]
		accClip = [slicepoints[i-1],fAcc[i-1],slicepoints[i]]
		subprocess.call(['C:/ffmpeg/bin/ffmpeg.exe','-i',startPresObj,'-ss',slicepoints[i-1],'-c','copy','-t',slicepoints[i],fPres[i-1]])
		subprocess.call(['C:/ffmpeg/bin/ffmpeg.exe','-i',startAccObj,'-ss',slicepoints[i-1], '-c','copy','-t',slicepoints[i],fAcc[i-1]])
	return
	

startPresObj = sys.argv[1]
startPresObj = startPresObj.replace("\\","/")
startAccObj = startPresObj.replace(".mxf",".mp4")
masterKey = sys.argv[2]
vmNums = ['vm0094','vm0095','vm0096']
slicepoints = ['00:00:59.90','00:11:59.13','00:27:01.57','00:31:06.50']
fPres, fAcc = makenames(masterKey, vmNums)
makeslices(fPres, fAcc, slicepoints, startPresObj, startAccObj)
