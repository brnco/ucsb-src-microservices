#!/usr/bin/env python
#coding=UTF-8
import os
import sys
import shutil
import time
import argparse
import ConfigParser
import getpass

def main():	
	#initialize all of the things
	#initialize arguments coming in from cli
	parser = argparse.ArgumentParser()
	parser.add_argument('-cyl','--cylinder',action='store_true',dest='cyl',default=False,help="make metadata file using cylinder template")
	parser.add_argument('-tape','--magneticTape',action='store_true',dest='tape',default=False,help="make metadata file using cylinder template")
	parser.add_argument('-disc','--disc',action='store_true',dest='disc',default=False,help="make metadata file using disc template")
	parser.add_argument('-so','--startObj',dest='so',help="the asset that we want to make metadata for")
	parser.add_argument('-t','--title',dest='t',default="",help="the tile of the asset, roughly the 245 |a field")	
	parser.add_argument('-a','--album',dest='a',default="",help="the intellectual parent unit of the start object")
	parser.add_argument('-p','--performer',dest='p',default="",help="the main talent on the object")
	parser.add_argument('-r','--rights',dest='r',default="©2016 The Regents of the University of California",help="a copyright statement for the asset")
	parser.add_argument('-d','--date',dest='d',default="",help="the four digit year in which the object was created")
	args = parser.parse_args()
	config = ConfigParser.ConfigParser()
	dn, fn = os.path.split(os.path.abspath(__file__)) #grip the path to the directory where ~this~ script is located
	config.read(os.path.join(dn,"microservices-config.ini"))
	
	if args.cyl is True: #for cylinders, do this
		captureDir = config.get("cylinders","new_ingest") #grab cylinder capture dir from config file
		startDir = os.path.join(captureDir,args.so) #complete the path to the capture dir
		mtdObj = os.path.join(startDir,"cusb-cyl" + args.so + "-mtd.txt") #init a metadata object
		pub = "UCSB Cylinder Audio Archive" #name the CAA as the publisher
		if not os.path.isdir(startDir): #if the dir doesn't exist let's not go lookin for it"
			print "Buddy, this cylinder hasn't been digitized yet"
			print "When it is digitized we'll worry about making ID3 tags for it"
			foo = raw_input("Press any key to quit")
			sys.exit()
	if args.tape is True: #for tapes do this
		archiveDir = config.get("magneticTape","repo") #grab archive directory for audio tapes
		endDirThousand = args.so.replace("a","") #input arg here is a1234 but we want just the number
		#the following separates out the first digit and assigns an appropriate number of zeroes to match our dir structure
		if len(endDirThousand) < 5:
			endDirThousand = endDirThousand[:1] + "000"
		else:
			endDirThousand = endDirThousand[:2] + "000"
		startDir = os.path.join(archiveDir,endDirThousand,args.so) #booshh
		if not os.path.isdir(startDir): #again, if it doesn't exists let's not chase it
			print "Buddy, this tape hasn't been digitized yet"
			print "When it is digitized we'll worry about making ID3 tags for it"
			foo = raw_input("Press any key to quit")
			sys.exit()
		mtdObj = os.path.join(startDir,"cusb-" + args.so + "-mtd.txt") #init a metadata object
		pub = "UCSB Library, Special Research Collections" #name SRC as publisher
	if args.disc is True:
		broadcastDir = config.get("discs","broadcastDir")
		mtdObj = os.path.join(broadcastDir,args.so + "-mtd.txt")
		pub = "UCSB Library, Special Research Collections"
		if not os.path.exists(os.path.join(broadcastDir,args.so + ".wav")):
			print "Buddy, this disc hasn't been digitized yet"
			print "When it is digitized we'll worry about making ID3 tags for it"
			foo = raw_input("Press any key to quit")
			sys.exit()
	#print that info to a text file in the FFMETADATA format	
	tf = open(mtdObj, "w")
	tf.write(";FFMETADATA1\ntitle=" + args.t + "\nalbum=" + args.a + "\nartist=" + args.p + "\ndate=" + args.d + "\npublisher=" + pub + "\ncopyright=" + args.r)
	tf.close()
	return

main()
