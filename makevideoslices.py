#!/usr/bin/env python
#splits a tape capture with n masters on it into individual files
#takes areguments for
#raw preservation capture file path
#master number, to triangulate the physical tape

import os
import subprocess
import sys
import glob
import ast
import argparse
import imp
from distutils import spawn

#check that we have the required software to run this script
def dependencies():
	depends = ['ffmpeg','ffprobe']
	for d in depends:
		if spawn.find_executable(d) is None:
			print "Buddy, you gotta install " + d
			sys.exit()


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

def makecomplexslices(fPres, fAcc, slicepoints, startPresObj, startAccObj):
	#build list of tuples here
	#[(vm0090, 4:08),(vm0091,6:00),...(vx1234,1:23)]
	#optional start time
	for i in range(1,len(slicepoints),1):
		presClip = [slicepoints[i-1],fPres[i-1],slicepoints[i]]
		accClip = [slicepoints[i-1],fAcc[i-1],slicepoints[i]]
		subprocess.call(['ffmpeg','-i',startPresObj,'-ss',slicepoints[i-1],'-c','copy','-t',slicepoints[i],fPres[i-1]])
		subprocess.call(['ffmpeg','-i',startAccObj,'-ss',slicepoints[i-1], '-c','copy','-t',slicepoints[i],fAcc[i-1]])

def makesimpleslice(args,startObj,startObjBoth,startDir,masterKey,ext):
	subprocess.call(['ffmpeg','-i',startObj,'-ss',args.i,'-t',args.o,'-c','copy',os.path.join(startDir,masterKey + "-sliced" + ext)])
	if startObjBoth:
		mk, ext = os.path.splitext(os.path.basename(startObjBoth))
		subprocess.call(['ffmpeg','-i',startObjBoth,'-ss',args.i,'-t',args.o,'-c','copy',os.path.join(startDir,masterKey + "-sliced" + ext)])


def main():
	###INIT VARS###
	dn, fn = os.path.split(os.path.abspath(__file__))
	global conf
	rawconfig = imp.load_source('config',os.path.join(dn,'config.py'))
	conf = rawconfig.config()
	global ut
	ut = imp.load_source("util",os.path.join(dn,"util.py"))
	global log
	log = imp.load_source('log',os.path.join(dn,'logger.py'))
	log.log("Started")
	parser = argparse.ArgumentParser(description="slices video into segments")
	parser.add_argument('-i','--startObj',dest='i',help='the full path of the file to be sliced')
	parser.add_argument('-m','--mode',dest='m',choices=['simple','complex'],help="mode, simple makes a single slice, complex takes a list - for video files with more than 1 vNumber in it")
	parser.add_argument('-db','--doBoth',dest='db',action='store_true',help="slice both preservation and access copies")
	parser.add_argument('-i','--in',dest='i',help="the start timestamp for the slice, HH:MM:SS.FF")
	parser.add_argument('-o','--out',dest='o',help="the end timestamp for the slice, HH:MM:SS.FF")
	parser.add_argument('-vms',dest='vms',help="list of vmNumbers (complex only)")
	parser.add_argument('-s','--slices',dest='s',help="list of slices (complex only)")
	args = parser.parse_args() #allows us to access arguments with args.argName
	startObj = args.i
	startObj = startObj.replace("\\","/")
	startObjBoth = ''
	masterKey,ext = os.path.splitext(os.path.basename(startObj))
	startDir = os.path.dirname(startObj)
	if args.db is True:
		if startObj.endswith(".mxf"):
			startObjBoth = startObj.replace("pres.mxf","acc.mp4")
		else:
			startObjBoth = startObj.replace("acc.mxf","pres.mp4")
	if args.m == 'complex':
		vmNums = ast.literal_eval(args.vms) #list of visual masters on the tape
		slicepoints = ast.literal_eval(args.s) #their in and out points
		fPres, fAcc = makenames(masterKey, vmNums) #calls the makenames function
		makecomplexslices(fPres, fAcc, slicepoints, startPresObj, startAccObj) #calls the slicing function
	else:
		makesimpleslice(args,startObj,startObjBoth,startDir,masterKey,ext)
dependencies()
main()