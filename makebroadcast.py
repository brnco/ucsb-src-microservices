#!/usr/bin/env python
#makebroadcast
#this script takes a single input file and makes a file suitable for broadcast/ delivery to patrons
#for audio this means 44.1kHz, 16bit, mono wav with ID3s (like a CD)
#for video this means a 6kbps H.264 .mp4
#you can also add fades or switch it to stereo
#"python makebroadcast.py -h" for help

import os
import subprocess
import sys
import glob
import re
import ast
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

def makeAudio(args, startObj, startDir, assetName, EuseChar):
	with cd(startDir):
		#set some defaults
		ac = '1' #audio channels
		ar = '44100' #audio rate
		sfmt = 's16' #sample_fmt, signed 16-bit in this case
		fadestring = '' #placeholder for fades, if we make em
		normstring = '' #placeholder for loudnorm
		if args['nationaljukebox'] is False: #sorts out the jukebox stuff which doesn't get this treatment
			id3string = makeid3(startDir, assetName) #calls our id3 function
		else:
			id3string = ''
		if args['normalize'] is True:
			normstring = "-af loudnorm=I=-16:TP=-1.5:LRA=11"
		#get the right channel config
		if args['stereo'] is not False:
			ac = '2'
		#lets make fades!
		if args['fades'] is not False:
			tmptxt = open(startObj + '.ffdata.txt','w')
			#pipe ffprobe data for only duration thru stdout to txt file
			subprocess.call(['ffprobe','-i',startObj,'-show_entries','format=duration','-v','quiet'], stdout = tmptxt)
			tmptxt.close()
			#read from that text file we just made
			ffdata = open(startObj + ".ffdata.txt","r")
			for line in ffdata:
				#import duration from ffprobe output
				if re.search('duration=', line):
					#split the line at the = sign, as output by ffprobe
					foolist = re.split(r'=', line)
					dur = foolist[1] #grab the text element that is the duration
					fadestart = float(dur) - 2.0 #subract 2 from that to get the fade out start time
					fadestart = str(fadestart)
					fadestring = "-af afade=t=in:ss=0:d=2,afade=t=out:st=" + fadestart + ":d=2 " #generate the fade string using the fade out start time
			ffdata.close() #housekeeping
			os.remove(startObj + '.ffdata.txt') #housekeeping
		#subprocess.call(['ffmpeg','-i',startObj,'-ar',ar,'-sample_fmt',sfmt,'-ac',ac,'-id3v2_version','3','-write_id3v1','1','-y',assetName + EuseChar + '.wav'])
		ffmpegstring = 'ffmpeg -i ' + startObj + " " + id3string + ' -ar ' + ar + ' -sample_fmt ' + sfmt + ' -ac ' + ac + ' ' + normstring + ' ' + fadestring + '-id3v2_version 3 -write_id3v1 1  ' + assetName + EuseChar + '.wav'
		subprocess.call(ffmpegstring)
		if args['mp3'] is True:
			subprocess.call(['python','S:/avlab/microservices/makemp3.py',assetName + EuseChar + '.wav'])
	return

#makes an id3 ;ffmetadata1 file that we can use to load tags into the broadcast master	
def makeid3(startDir, assetName):
	id3fields=["title=","artist=","date="]
	match = ''
	match = re.search("a\d{4,5}",assetName) #grip jsut the a1234 part of the filename
	if match:
		assetName = match.group()
	id3rawlist = subprocess.check_output(["python","S:/avlab/microservices/fm-stuff.py","-so",assetName.capitalize(),"-id3"])
	id3rawlist = ast.literal_eval(id3rawlist)
	id3str = ""
	for index, tag in enumerate(id3rawlist):
		if tag is not None:
			id3str = id3str + " -metadata " + id3fields[index] + '"' + tag + '"'
	print id3str
	foo = raw_input("eh")
	return id3str

#parses input and makes the appropriate calls	
def handling():
	#initialize a buncha crap
	parser = argparse.ArgumentParser(description="Makes a broadcast-ready file from a single input file")
	parser.add_argument('startObj',nargs ='?',help='the file to be transcoded',)
	parser.add_argument('-ff','--fades',action='store_true',default=False,help='adds 2s heads and tails fades to black/ silence')
	parser.add_argument('-s','--stereo',action='store_true',default=False,help='outputs to stereo (mono is default)')
	parser.add_argument('-mp3','--mp3',action='store_true',default=False,help='make an mp3 when done making a broadcast master')
	parser.add_argument('-n','--normalize',action='store_true',default=False,help='EBU r128 normalization with true peaks at -1.5dB, defaults to off')
	parser.add_argument('-nj','--nationaljukebox',action='store_true',default=False,help='extra processing step for National Jukebox files')
	parser.add_argument('-njnd','--njnodelete',action="store_true",default=False,help="don't delete startObjs for nj files, useful for making broadcasts from m.wavs")
	args = vars(parser.parse_args()) #create a dictionary instead of leaving args in NAMESPACE land
	startObj = args['startObj'].replace("\\",'/') #for the windows peeps
	vexts = ['.mxf','.mp4','.mkv'] #set extensions we recognize for video
	aexts = ['.wav'] #set extensions we recognize for audio
	fnamext = os.path.basename(os.path.abspath(startObj)) #grabs the filename and extension
	fname, ext = os.path.splitext(fnamext) #splits filename and extension
	SuseChar = fname[-1:] #grabs the last char of file name which is ~sometimes~ the use character
	startDir = os.path.abspath(os.path.join(startObj, os.pardir)) #grabs the directory that this object is in (we'll cd into it later)
	#start testing
	if not os.path.isfile(startObj): #if it's not a file, say so
		print "Buddy, that's not a file"
	if not ext in vexts and not ext in aexts: #if it's not a file we expect to deal with, say so, it probly needs special params
		print "Buddy, that's not really a file that we can make a broadcast master out of"
	else:
		if ext in vexts:
			print "itsa vid"
			#makevideo(startObj, ) gotta get on this
		if ext in aexts:
			print "itsa sound"
			#see what character it is and assign EndUseCharacters accordingly
			if SuseChar == 'a':
				print "archival master"
				assetName = fname[:-1]
				EuseChar = "b"
			elif SuseChar == 'm':
				print "archival master"
				assetName = fname[:-1]
				EuseChar = ""
			elif SuseChar == 'b':
				print "broadcast master"
				assetName = fname[:-1]
				EuseChar = 'c'
			elif SuseChar == 'c':
				assetName = fname[:-1]
				EuseChar = "e"
			else:
				assetName = fname
				EuseChar = "b"
			makeAudio(args, startObj, startDir, assetName, EuseChar) #actually make the thing
	if SuseChar == 'b':
		with cd (startDir):
			if os.path.exists(assetName + "b.wav") and os.path.exists(assetName + "c.wav"):
				os.remove(assetName + "b.wav")
				os.rename(assetName + "c.wav", assetName + "b.wav")
	if args['nationaljukebox'] is True:
		with cd(startDir):
			if args["njnodelete"] is False:
				os.remove(startObj)
			os.rename(assetName + EuseChar + '.wav',assetName + '.wav')
	return 


dependencies()
handling()

#adds for later
#seeing if id3 metadata is already in the file, import from makemp3
#replacing print to txt with regex
#video