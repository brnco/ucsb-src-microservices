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
	parser.add_argument('-cyl','--cylinder',action='store_true',dest='c',default=False,help="make metadata file using cylinder template")
	parser.add_argument('-so','--startObj',dest='so',help="the asset that we want to make metadata for")
	parser.add_argument('-t','--title',dest='t',help="the tile of the asset, roughly the 245 |a field")	
	parser.add_argument('-a','--album',dest='a',help="the intellectual parent unit of the start object")
	parser.add_argument('-p','--performer',dest='p',help="the main talent on the object")
	parser.add_argument('-r','--rights',dest='r',default="©2016 The Regents of the University of California",help="a copyright statement for the asset")
	parser.add_argument('-d','--date',dest='d',help="the four digit year in which the object was created")
	args = parser.parse_args()
	config = ConfigParser.ConfigParser()
	config.read("C:/Users/" + getpass.getuser() + "/microservices-config.ini")
	
	if args.c is True:
		captureDir = config.get("cylinders","cylCaptureDir")
		startDir = os.path.join(captureDir,args.so)
		mtdObj = os.path.join(startDir,"cusb-cyl" + args.so + "-mtd.txt")
		pub = "UCSB Cylinder Audio Archive"
		if not os.path.isdir(startDir):
			print "Buddy, this cylinder hasn't been digitized yet"
			print "When it is digitized we'll worry about making ID3 tags for it"
			foo = raw_input("Press any key to quit")
			sys.exit()
	tf = open(mtdObj, "w")
	tf.write(";FFMETADATA1\ntitle=" + args.t + "\nalbum=" + args.a + "\nartist=" + args.p + "\ndate=" + args.d + "\npublisher=" + pub + "\ncopyright=" + args.r)
	tf.close()
	return

main()
