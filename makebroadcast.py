#!/usr/bin/env python
#makebroadcast
#this script takes a single input file and makes a file suitable for broadcast/ delivery to patrons
#for audio this means 44.1kHz, 16bit, mono wav with ID3s (like a CD)
#for video this means a 6kbps H.264 .mp4
#you can also add fades or switch it to stereo
#"python makebroadcast.py -h" for help

import os
from subprocess import PIPE
import subprocess
import sys
import glob
import re
import ast
import time
import argparse
import imp
from bs4 import UnicodeDammit
from distutils import spawn

#check that we have required software installed
def dependencies():
	depends = ['ffmpeg','ffprobe']
	for d in depends:
		if spawn.find_executable(d) is None:
			print "Buddy, you gotta install " + d
			sys.exit()
	return

def makeVideo(startObj):
	#print ffprobe output to txt file, we'll grep it later to see if we need to transcode for j2k/mxf
	ffdata = open(startObj + ".ffdata.txt","w")
	subprocess.call(['ffprobe','-show_streams','-of','flat','-sexagesimal','-i',startObj], stdout=ffdata)
	ffdata.close()

	#find which stream is the video stream
	ffdata = open(startObj + ".ffdata.txt","r")
	for line in ffdata:
		#find the line for video stream
		if re.search('.codec_type=\"video\"', line):
			#separate that line by periods, the formatting provided by ffprobe
			foolist = re.split(r'\.', line)
			#3rd part of that list is the video stream
			whichStreamVid = foolist[2]
		#find the line for audio stream
		if re.search('.codec_type=\"audio\"', line):
			#separate that line by periods, the formatting provided by ffprobe
			foolist = re.split(r'\.', line)
			#3rd part of that list is the video stream
			whichStreamAud = foolist[2]
			print whichStreamAud
	ffdata.close()
	return

def makeAudio(args, startObj, startDir, assetName, SuseChar, EuseChar):
	with ut.cd(startDir):
		####INIT VARS###
		#ac = '1' #audio channels
		ar = '44100' #audio rate
		acodec = 'pcm_s16le' #sample_fmt, signed 16-bit little-endian
		fadestring = '' #placeholder for fades, if we make em
		normstring = '' #placeholder for loudnorm
		filterstring = '' #placeholder for -af + fadestring + loudnorm
		###END INIT###
		###MAKE ID3 TAGS###
		if args.nj is False: #sorts out the jukebox stuff which doesn't get this treatment
			if args.t is True:
				id3string = gettapeid3(startDir, assetName) #calls our id3 function
			elif args.d is True:
				if not args.sys:
					print 'Buddy, you need to submit a system number "-sys" to get the id3 tags from our catalog'
					sys.exit()
				id3string = getdiscid3(args,assetName)
			elif args.c is True:
				id3string = getcylinderid3(args,assetName)
			else:
				id3string = makemanualid3(startDir,assetName)
		else:
			id3string = ''
		###END ID3 TAGS###
		###OTHER OPTIONS###
		if args.n is True:#for normalize
			normstring = "loudnorm=I=-16:TP=-1.5:LRA=11"
		#if args.s is True:#get the right channel config
			#ac = '2'
		if args.ff is True:#lets make fades!
			ffprobeout = subprocess.check_output(['ffprobe','-i',startObj,'-show_entries','format=duration','-v','quiet']) #get duration from ffprobe
			match=''
			match=re.search('\d*\.\d*',ffprobeout) #find the duration in seconds.milliseconds from the ffprobeout string
			if match:
				dur = match.group() #convert the re object to a string, assign to duration variable
				fadestart = float(dur) - 2.0 #subract 2 from that to get the fade out start time
				fadestring = "afade=t=in:ss=0:d=2,afade=t=out:st=" + str(fadestart) + ":d=2" #generate the fade string using the fade out start time
		###END OTHER OPTIONS
		###GET IT TOGETHER###
		if fadestring and normstring:
			filterstring = "-af " + fadestring + "," + normstring
		elif fadestring and not normstring:
			filterstring = "-af " + fadestring
		elif normstring and not fadestring:
			filterstring = "-af " + normstring
		ffmpegstring = 'ffmpeg -i ' + startObj + " " + id3string + ' -ar ' + ar + ' -c:a ' + acodec + ' ' + filterstring + ' -id3v2_version 3 -write_id3v1 1 -write_bext 1 ' + assetName + EuseChar + '.wav'
		#_ffmpegstring = ffmpegstring.decode("utf-8")
		#ffmpegstring = _ffmpegstring.encode("ascii","ignore")
		#print ffmpegstring
		subprocess.call(ffmpegstring)
		cleanup(args,SuseChar,EuseChar,startDir,startObj,assetName) #rename and delete as necessary
		time.sleep(4)
		if args.mp3 is True:
			subprocess.call(['python',os.path.join(conf.scriptRepo,'makemp3.py'),'-so',startObj])
	return

#makes an id3 ;ffmetadata1 file that we can use to load tags into the broadcast master	
def makemanualid3(startDir, assetName):
	###INIT VARS###
	if assetName.endswith("A") or assetName.endswith("B"):
		assetName = assetName[:-1]
	id3Obj = os.path.join(startDir, assetName + "-mtd.txt") #in same dir as audio object should be a -mtd.txt object with a ;FFMETADATA1 id3 tags inside
	id3String = ""
	###END INIT###
	###USER ID3###
	if not os.path.exists(id3Obj): #check to see if it exists alread
		usrInput = ''
		while usrInput not in ['y','n']: #gotta answer yes or no to this q
			usrInput = raw_input("There is currently no associated ID3 metadata for this object, would you like to make some so that it'll play nice with iTunes? (y/n) ")
			usrInput = usrInput.lower()
		#this promts the user to make a txt file with this formatting
		if usrInput == 'y':
			print " "
			print "Great, thank you! Here's how"
			print "1)Open a new text file and save it in the same folder as the thing you're trying to broadcast"
			print "2)Type the following into the empty text file, keep the new lines and punctuation"
			print ";FFMETADATA1"
			print "title= "
			print "artist= "
			print "album= "
			print "date= "
			print "publisher=UCSB Special Research Collections"
			print " "
			print "3)Ok, don't type this part. Now, the best you can, fill out those fields in the text file"
			print "4)Lastly, save it as " + assetName + "-mtd.txt"
			donezo = raw_input("Press 'Enter' when you've finished the above process") #pauses script until the user says they're done
			id3String = "-i " + id3Obj + " -map_metadata 1" #set the string so ffmpeg can find and use this obj
		if usrInput == 'n':
			print "Ok, not great but ok" #fine, i mean i guess, whatever
			time.sleep(5)
	###END USER ID3###
	###GET IT TOGETHER###
	else:
		id3String = "-i " + id3Obj + " -map_metadata 1" #if the object already exists, set the string so ffmpeg can find and use this obj
	return id3String	
	
#grips id3 info from FileMaker
def gettapeid3(startDir, assetName):
	id3fields=["title=","artist=","date="] #set the fields we need for this object type
	match = ''
	match = re.search("a\d{4,5}",assetName) #grip just the a1234 part of the filename
	if match:
		assetName = match.group()
	id3rawlist = subprocess.check_output(["python",os.path.join(conf.scriptRepo,"fm-stuff.py"),"-so",assetName.capitalize(),"-id3","-t"]) #ask filemaker for the value for each field
	id3rawlist = ast.literal_eval(id3rawlist) #convert the string coming back from FM to an actual python tuple
	id3str = makeid3str(id3fields,id3rawlist,assetName)
	return id3str

def getcylinderid3(args,assetName):
	id3fields=["title=","artist=","composer=","album=","date="] #set the fields we need for this object type
	id3str = ''
	match = ''
	match = re.search(r"\d{4,5}",assetName) #grip just the number of the cylinder
	if match:
		assetName = match.group()
	id3rawlist = subprocess.check_output(["python",os.path.join(conf.scriptRepo,"fm-stuff.py"),"-so",assetName.replace("cusb-cyl",""),"-id3","-c"]) #ask filemaker for the values for each field
	id3rawlist = ast.literal_eval(id3rawlist) #convert the string coming back from FM to an actual python tuple
	id3str = makeid3str(id3fields,id3rawlist,assetName)
	return id3str	
	
def getdiscid3(args,assetName):
	id3fields=["title=","artist=","date="] #set the fields we need for this object type
	id3str = ""
	output = subprocess.Popen(["python",os.path.join(conf.scriptRepo,"catalog-stuff.py"),"-sys",args.sys],stdout=PIPE,stderr=PIPE) #ask the catalog for the values for each field
	id3rawlist1 = output.communicate() #convert from output object to string
	###1 SIDE OR 2###
	#discs can have multiple values come back from catalog-stuff
	#this next bit sorts that out, as we're just working with 1 single object
	match = ''
	#search first part of catalog-stuff tuple for everything within the brackets
	match = re.findall("\[.*\]",id3rawlist1[0])
	if match:
		#convert to tuple
		id3list1 = ast.literal_eval(match[0])
		try:
			#see if we can convert the second found set in the catalog-stuff output into a tuple
			id3list2 = ast.literal_eval(match[1])
		except:
			pass
	elements = assetName.split('_') #splits the disc filename by underscore into a list
	matrixNumber = elements[-2] #second from the last underscore-separated value is always the matrix number
	if matrixNumber in id3list1[-1]: #if the matrix number is in id3list1, then set the output id3list to it
		id3list = id3list1
	elif matrixNumber in id3list2[-1]: #if the matrix number is in id3list2, then set the output id3list to it instead
		id3list = id3list2
	else: #if we can't find the matrix number in the catalog record
		if args.side is None: #if the user didn't specify
			print "Buddy, you need to specify which side of the disc we're working on"
			sys.exit()
		else: #if the user specified, set it this way
			if args.side.capitalize()=="A":
				id3list = id3list1
			if args.side.capitalize()=="B":
				id3list = id3list2
			else:
				print "Buddy, the side you specified is outta range. Use A or B instead"
	id3str = makeid3str(id3fields,id3list,assetName) #make a thing that ffmpeg understands
	return id3str

def makeid3str(id3fields,id3rawlist,assetName): #take the tag names and values and make them into something ffmpeg understands
	id3str = ''
	for index, tag in enumerate(id3fields): #loop thru the raw list of id3 values, grip the index
		if tag is not None:
			if id3rawlist[index] is not None:
				id3str = id3str + " -metadata " + tag + '"' + id3rawlist[index].replace('"','') + '"'
				#^append the tag from the list of id3fields and the value from the corresponding index in the raw list of values
	if not "album=" in id3fields:
		id3str = id3str + ' -metadata album="' + assetName + '" -metadata publisher="UCSB Special Research Collections"'
		#^make sure we don't leave the album blank it's my fave way to sort in iTunes
	else:
		id3str = id3str + ' -metadata publisher="UCSB Special Research Collections"'
		#^make sure the ppl know where thsi good stuff came from
	#print id3str
	id3str = UnicodeDammit.detwingle(id3str)
	#print id3str
	return id3str

def makeEuseChar(SuseChar, fname): #makes the end use character for the output file
	#end use characters correspond to different parts of our OAIS implementation
	#filenames ending in "a" are our archival masters
	#filenames ending in "b" are our broadcast masters
	#filenames ending in "c" are intermediate files
	#filenames ending in "d" are access files
	if SuseChar == 'a':
		assetName = fname[:-1]
		EuseChar = "b"
	elif SuseChar == 'm':
		assetName = fname[:-1]
		EuseChar = ""
	elif SuseChar == 'b':
		assetName = fname[:-1]
		EuseChar = 'c'
	elif SuseChar == 'c':
		assetName = fname[:-1]
		EuseChar = "e"
	else:
		assetName = fname
		EuseChar = "b"
	return EuseChar, assetName
	
def cleanup(args,SuseChar,EuseChar,startDir,startObj,assetName): #deletes and renames stuff if the operation was successful
	if SuseChar == 'b': #if we made a broadcast amster from a raw broadcast master
		with ut.cd(startDir):
			if os.path.exists(assetName + "b.wav") and os.path.exists(assetName + "c.wav"):
				if args.nd is False: #if we didn't say not to delete it
					os.remove(assetName + "b.wav")
					os.rename(assetName + "c.wav", assetName + "b.wav")
	if args.nj is True:
		with ut.cd(startDir):
			if args.nd is False:
				os.remove(startObj)
			os.rename(assetName + EuseChar + '.wav',assetName + '.wav')

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
	parser = argparse.ArgumentParser(description="Makes a broadcast-ready file from a single input file")
	parser.add_argument('-so','--startObj',dest='so',nargs ='?',help='the file to be transcoded, can be full path or assetname, e.g. a1234, cusb_col_a123_01_456_00')
	parser.add_argument('-ff','--fades',dest='ff',action='store_true',default=False,help='adds 2s heads and tails fades to black/ silence')
	#parser.add_argument('-s','--stereo',dest='s',action='store_true',default=False,help='outputs to stereo (mono is default)')
	parser.add_argument('-mp3','--mp3',dest='mp3',action='store_true',default=False,help='make an mp3 when done making a broadcast master')
	parser.add_argument('-n','--normalize',dest='n',action='store_true',default=False,help='EBU r128 normalization with true peaks at -1.5dB, defaults to off')
	parser.add_argument('-nj','--nationaljukebox',dest='nj',action='store_true',default=False,help='extra processing step for National Jukebox files')
	parser.add_argument('-nd','--nodelete',dest='nd',action="store_true",default=False,help="don't delete startObjs for nj files, useful for making broadcasts from m.wavs")
	parser.add_argument('-t','--tape',dest='t',action='store_true',default=False,help='use settings for "tape", get id3 metadata from FileMaker')
	parser.add_argument('-d','--disc',dest='d',action='store_true',default=False,help='use settings for "disc",get id3 metadata from Pegasus catalog')
	parser.add_argument('-c','--cylinder',dest='c',action='store_true',default=False,help='use settings for "cylinder", get id3 metadata from FileMaker')
	parser.add_argument('-sys','--systemNumber',dest='sys',help='the system number in Pegasus of the disc for which you want id3 tags')
	parser.add_argument('-side',dest='side',help='the side of the disc (aA or bB) that we are working with, for catalog records w/out matrix numbers')
	args = parser.parse_args() #allows us to access arguments with args.argName
	startObj = subprocess.check_output(["python",os.path.join(conf.scriptRepo,"makestartobject.py"),"-so",args.so])
	startObj = startObj.replace("\\","/")[:-2]
	vexts = ['.mxf','.mp4','.mkv'] #set extensions we recognize for video
	aexts = ['.wav'] #set extensions we recognize for audio
	fnamext = os.path.basename(os.path.abspath(startObj)) #grabs the filename and extension
	fname, ext = os.path.splitext(fnamext) #splits filename and extension
	SuseChar = fname[-1:] #grabs the last char of file name which is ~sometimes~ the use character
	startDir = os.path.abspath(os.path.join(startObj, os.pardir)) #grabs the directory that this object is in (we'll cd into it later)
	###END INIT###
	
	###VALIDATE INPUT###
	#if not os.path.isfile(startObj): #if it's not a file, say so
		#print "Buddy, that's not a file"
	if not ext in vexts and not ext in aexts: #if it's not a file we expect to deal with, say so, it probly needs special params
		print "Buddy, this file can't be processed by makebroadcast"
	###END VALIDATE###
	
	###DO THE THING###
	#elif ext in vexts:
		#makevideo(startObj, ) gotta get on this
	if ext in aexts:
		EuseChar, assetName = makeEuseChar(SuseChar,fname) #grip the right filename endings, canonical name of the asset
		makeAudio(args, startObj, startDir, assetName, SuseChar, EuseChar) #actually make the thing
	
	###THINGISDONE###

dependencies()
main()