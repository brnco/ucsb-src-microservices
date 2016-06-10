#makebext
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
	#parser.add_argument('-cyl','--cylinder',action='store_true',dest='cyl',default=False,help="make metadata file using cylinder template")
	parser.add_argument('-tape','--magneticTape',action='store_true',dest='tape',default=False,help="make metadata file using tape template")
	#parser.add_argument('-disc','--disc',action='store_true',dest='disc',default=False,help="make metadata file using disc template")
	parser.add_argument('-so','--startObj',dest='so',help="the asset that we want to make metadata for")
	parser.add_argument('-d','--date',dest='m',default="",help="'mastered' from FM, the date this asset was digitized")	
	parser.add_argument('-mk','--masterKey',dest='mk',default="",help="5 digit number linking the file to a physical object in FM")
	parser.add_argument('-t','--title',dest='t',default="",help="the title of the object in FM")
	parser.add_argument('-mss','--mss',dest='mss',default="",help="the collection number/code of the object")
	parser.add_argument('-c','--collection',dest='c',default="",help="the collection name of the object")
	args = parser.parse_args()
	config = ConfigParser.ConfigParser()
	config.read("C:/Users/" + getpass.getuser() + "/microservices-config.ini")

	if args.tape is True: #for tapes do this
		startDir = config.get("magneticTape","magTapebexts")
		mtdObj = os.path.join(startDir,"cusb-" + args.so + "-bext.txt") #init a metadata object
		originator = "US,CUSB,SRC"
		originatorRef = "cusb-" + args.so
		description = "Audio Number: " + args.so + "; MSS Number: " + args.mss + "; Collection: " + args.c + "; Tape Title: " + args.t + "; Master Key: " + args.mk
		if len(description) > 255:
			description = description[:255]
		f = open(mtdObj,'w')
		f.write('--Originator=' + originator + ' --originatorReference=' + originatorRef + ' --Description="' + description + '"')
		#this string is called by our tape processing script, it's concatenated with a bwfmetaedit call
		f.close()

	return

main()