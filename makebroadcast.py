#!/usr/bin/env python
'''
makebroadcast
this script takes a single input file and makes a file suitable for broadcast/ delivery to patrons
for audio this means 44.1kHz, 16bit, mono wav with ID3s (like a CD)
for video this means a 6kbps H.264 .mp4
you can also add fades or switch it to stereo
'''

import os
from subprocess import PIPE
import subprocess
import sys
import glob
import re
import ast
import time
import argparse
###UCSB modules###
import config as rawconfig
import util as ut
import logger as log
import mtd
import ff
import makestartobject as makeso

def concat_vobs(file):
	'''
	concatenates VOB files into single VOB
	'''
	'''with open(file.concatxt, 'a') as concat:
		for vob in os.listdir(file.vobDir):
			if vob.startswith('VTS') and vob.endswith('.VOB'):
				concat.write("file '" + vob + "'\n")
	ffstr = 'ffmpeg -f concat -i concat.txt -c copy -map V -map a ' + file.vobOutFullPath'''
	inputstr = ''
	inputcount = 0
	filterstrprefix = ''
	for vob in os.listdir(file.vobDir):
		if vob.startswith('VTS') and vob.endswith('.VOB'):
			inputstr = inputstr + " -i " + vob
			filterstrprefix = filterstrprefix + "[" + str(inputcount) + ":v:0] [" + str(inputcount) + ":a:0] "
			inputcount = inputcount + 1
	ffstr = 'ffmpeg' + inputstr + ' -filter_complex "' + filterstrprefix + ' concat=n=' + str(inputcount) + ':v=1:a=1 [v] [a]" -map "[v]" -map "[a]" -c:v libx264 -movflags faststart -pix_fmt yuv420p -crf 20 -c:a aac -ac 2 -b:a 192k ' + file.outputFullPath
	print ffstr
	foo = raw_input("eh")
	with ut.cd(file.vobDir):
		ffWorked = ff.go(ffstr)
		if ffWorked is not True:
			print 'makebroadcast encountered the following error trying to concatenate the VOBs'
			print ffWorked
			return False
		else:
			return True

def make_video(args):
	'''
	handles making broadcast masters from VIDEO_TS DVD/ VOB files
	'''
	file = ut.dotdict({})
	file.vobDir = args.i
	file.vNum = os.path.basename(os.path.dirname(file.vobDir))
	file.name = 'cusb-' + file.vNum
	file.vobOutFullPath = os.path.join(os.path.dirname(file.vobDir), file.name + '-concat.VOB')
	file.outputFullPath = os.path.join(os.path.dirname(file.vobDir), file.name + '-acc.' + conf.ffmpeg.vcodec_access_format)
	file.concatxt = os.path.join(file.vobDir, 'concat.txt')
	worked = concat_vobs(file)
	#worked = True
	if worked is not True:
		print 'makebroadcast encountered an error'
		sys.exit()

def make_audio(args, thefile):
	'''
	process audio objects into broadcast masters
	'''
	ar = conf.ffmpeg.acodec_broadcast_rate #audio rate
	acodec = conf.ffmpeg.acodec_broadcast #sample_fmt, signed 16-bit little-endian
	fadestring = '' #placeholder for fades, if we make em
	normstring = '' #placeholder for loudnorm
	filterstring = '' #placeholder for -af + fadestring + loudnorm
	id3string = id3_handler(args, thefile)

	if args.n is True:
		'''
		grips the normalize string
		'''
		normstring = conf.ffmpeg.filter_loudnorm

	#if args.s is True:#get the right channel config
		#ac = '2'

	if args.f is True:
		'''
		makes the fadestring
		'''
		streams = ff.probe_streams(thefile.infullpath)
		fadestart = float(streams['0.duration']) - 2.0
		fadestring = "afade=t=in:ss=0:d=2,afade=t=out:st=" + str(fadestart) + ":d=2" #generate the fade string using the fade out start time

	###GET IT TOGETHER###
	if fadestring and normstring:
		filterstring = "-af " + fadestring + "," + normstring
	elif fadestring or normstring:
		filterstring = "-af " + fadestring + normstring
	ffmpegstring = 'ffmpeg -i ' + thefile.infullpath + " " + id3string + ' -ar ' + ar + ' -c:a ' + acodec + ' ' + filterstring \
	+ ' ' + conf.ffmpeg.acodec_writeid3 + ' ' + conf.ffmpeg.acodec_master_writebext + ' -y ' + thefile.outfullpath
	#_ffmpegstring = ffmpegstring.decode("utf-8")
	#ffmpegstring = _ffmpegstring.encode("ascii","ignore")
	#print ffmpegstring
	ffWorked = ff.go(ffmpegstring)
	if ffWorked is True:
		cleanup(args, thefile) #rename and delete as necessary
		time.sleep(4)
	else:
		print "makebroadcast encountered an error transcoding that file"
		print ffWorked

def id3_handler(args, thefile):
	'''
	assigns functions based on ID3 needs
	'''
	if args.nj is False: #sorts out the jukebox stuff which doesn't get this treatment
		if args.t is True:
			id3string = make_tapeid3(thefile.dir, thefile) #calls our id3 function
		elif args.c is True:
			id3string = make_cylinderid3(args, thefile)
		elif args.d is True:
			if not args.sys:
				print 'Buddy, you need to submit a system number "-sys" to get the id3 tags from our catalog'
				sys.exit()
			id3string = make_discid3(args, thefile)
		else:
			id3string = mtd.make_manualid3(thefile)
	else:
		id3string = ''
	return id3string

def make_tapeid3(args, thefile):
	'''
	make id3 lists for tape objects
	'''
	id3fields=["title=","artist=","date="] #set the fields we need for this object type
	kwargs = {"aNumber":thefile.aNumber}
	id3rawlist = mtd.get_tape_ID3(conf.magneticTape.cnxn, **kwargs) #ask filemaker for the value for each field
	id3str = mtd.make_id3str({"id3fields":id3fields, "id3rawlist":id3rawlist, "assetName":thefile.aNumber})
	return id3str

def make_cylinderid3(args, thefile):
	'''
	make id3 lists for cylinder objects
	'''
	id3fields=["title=","artist=","composer=","album=","date="] #set the fields we need for this object type
	kwargs = {"cylNumber":thefile.cylNumber}
	id3rawlist = mtd.get_cylinder_ID3(conf.cylinders.cnxn,**kwargs) #ask filemaker for the values for each field
	id3str = mtd.make_id3str({"id3fields":id3fields, "id3rawlist":id3rawlist, "assetName":thefile.cylNumber})
	return id3str

def make_discid3(args, thefile):
	'''
	make id3 lists for disc objects
	'''
	id3fields=["title=","artist=","date="] #set the fields we need for this object type
	id3str = ""
	soup = mtd.query_catalog(args.sys)
	id3dict1, id3dict2 = mtd.make_ID3fromCatalogSoup(soup)
	elements = thefile.assetName.split('_') #splits the disc filename by underscore into a list
	matrixNumber = elements[-2] #second from the last underscore-separated value is always the matrix number
	if matrixNumber in id3dict1['label']: #if the matrix number is in id3list1, then set the output id3list to it
		id3dict = id3dict1
	elif matrixNumber in id3dict2['label']: #if the matrix number is in id3list2, then set the output id3list to it instead
		id3dict = id3dict2
	else: #if we can't find the matrix number in the catalog record
		if args.side is None: #if the user didn't specify
			print "Buddy, you need to specify which side of the disc we're working on"
			sys.exit()
		else: #if the user specified, set it this way
			if args.side.capitalize() == "A":
				id3dict = id3dict1
			if args.side.capitalize() == "B":
				id3dict = id3dict2
			else:
				print "Buddy, the side you specified is outta range. Use A or B instead"
	id3rawlist = []
	for id3tag in id3fields:
		id3rawlist.append(id3dict[id3tag.replace("=",'')])
	id3str = mtd.make_id3str({"id3fields":id3fields,"id3rawlist":id3rawlist,"assetName":thefile.assetName}) #make a thing that ffmpeg understands
	return id3str

def make_endUseChar(thefile): #makes the end use character for the output file
	'''
	end use characters correspond to different parts of our OAIS implementation
	filenames ending in "a" are our archival masters
	filenames ending in "b" are our broadcast masters
	filenames ending in "c" are intermediate files
	filenames ending in "d" are access files
	'''
	se = {"a":"b", "b":"c", "c":"e"} #start:end character rules
	thefile.endUseChar = ''
	for s in se:
		if thefile.startUseChar == s:
			thefile.endUseChar = se[s]
			thefile.assetName = thefile.fname[:-1]
	if not thefile.endUseChar:
		thefile.endUseChar = 'b'
		thefile.assetName = thefile.fname
	return thefile

def cleanup(args, thefile): #deletes and renames stuff if the operation was successful
	'''
	rename things
	'''
	if args.nj is True:
		if args.nd is False:
			os.remove(thefile.infullpath)
		time.sleep(2.0)
		os.rename(os.path.join(thefile.dir, thefile.assetName + thefile.endUseChar + '.wav'), thefile.infullpath)
	else:
		if thefile.startUseChar == 'b': #if we made a broadcast master from a raw broadcast master
			if os.path.exists(thefile.assetName + "b.wav") and os.path.exists(thefile.assetName + "c.wav"):
				if args.nd is False: #if we didn't say not to delete it
					print "os.remove " + thefile.assetName + "b.wav"
					os.remove(thefile.assetName + "b.wav")
					print "os.rename " + thefile.assetName + "c.wav" + " " + thefile.assetName + "b.wav"
					os.rename(thefile.assetName + "c.wav", thefile.assetName + "b.wav")


def parse_input(args):
	'''
	makes a dictionary of file attributes
	'''
	thefile = ut.dotdict({})
	startObj = subprocess.check_output([conf.python,os.path.join(conf.scriptRepo,"makestartobject.py"),"-i",args.i])
	thefile.infullpath = startObj.replace("\\","/").strip()
	thefile.fname, thefile.ext = os.path.splitext(os.path.basename(os.path.abspath(thefile.infullpath))) #splits filename and extension
	thefile.startUseChar = thefile.fname[-1:] #grabs the last char of file name which is ~sometimes~ the use character
	thefile.dir = os.path.dirname(thefile.infullpath) #grabs the directory that this object is in (we'll cd into it later)
	if args.nj is False:
		thefile = make_endUseChar(thefile) #grip the right filename endings, canonical name of the asset
	else:
		thefile.endUseChar = "x"
		thefile.assetName = thefile.fname
	thefile.outfname = thefile.assetName + thefile.endUseChar + "." + conf.ffmpeg.acodec_broadcast_format
	thefile.outfullpath = os.path.join(thefile.dir, thefile.outfname)
	if args.t:
		match = ''
		match = re.search("a\d{4,5}",thefile.assetName) #grip just the a1234 part of the filename
		if match:
			thefile.aNumber = match.group()
	elif args.c:
		match = ''
		match = re.search(r"\d{4,5}",thefile.assetName) #grip just the number of the cylinder
		if match:
			thefile.cylNumber = match.group()
	return thefile

def init_args():
	'''
	initialize arguments from the cli
	'''
	parser = argparse.ArgumentParser(description="Makes a broadcast-ready file from a single input file. audio only for now")
	parser.add_argument('-i', '--startObj', dest='i',nargs ='?', help='the file to be transcoded, can be full path or assetname, e.g. a1234, cusb_col_a123_01_456_00')
	parser.add_argument('-f', '--fades', dest='f', action='store_true', default=False, help='adds 2s heads and tails fades to black/ silence')
	#parser.add_argument('-s','--stereo',dest='s',action='store_true',default=False,help='outputs to stereo (mono is default)')
	parser.add_argument('-mp3', '--mp3', dest='mp3', action='store_true', default=False, help='make an mp3 when done making a broadcast master')
	parser.add_argument('-n', '--normalize', dest='n', action='store_true', default=False, help='EBU r128 normalization with true peaks at -1.5dB, defaults to off')
	parser.add_argument('-nj', '--nationaljukebox', dest='nj',action='store_true', default=False, help='extra processing step for National Jukebox files')
	parser.add_argument('-nd', '--nodelete', dest='nd',action="store_true", default=False, help="don't delete startObjs for nj files, useful for making broadcasts from m.wavs")
	parser.add_argument('-t', '--tape', dest='t', action='store_true', default=False, help='use settings for "tape", get id3 metadata from FileMaker')
	parser.add_argument('-d', '--disc', dest='d', action='store_true', default=False, help='use settings for "disc",get id3 metadata from Pegasus catalog')
	parser.add_argument('-c', '--cylinder', dest='c', action='store_true', default=False, help='use settings for "cylinder", get id3 metadata from FileMaker')
	parser.add_argument('-sys', '--systemNumber', dest='sys', help='the system number in Pegasus of the disc for which you want id3 tags')
	parser.add_argument('-side', dest='side', help='the side of the disc (aA or bB) that we are working with, for catalog records w/out matrix numbers')
	args = parser.parse_args() #allows us to access arguments with args.argName
	return args

def main():
	'''
	do the thing
	'''
	global conf
	conf = rawconfig.config()
	args = init_args()
	if "VIDEO_TS" in args.i:
		make_video(args)
	else:
		thefile = parse_input(args)
		aexts = ['.wav'] #set extensions we recognize for audio
		if not os.path.exists(thefile.infullpath): #if it's not a file, say so
			print "Buddy, that's not a file"
		###DO THE THING###
		elif thefile.ext in aexts:
			with ut.cd(thefile.dir):
				make_audio(args, thefile) #actually make the thing
				if args.mp3 is True:
					subprocess.call(["python",os.path.join(conf.scriptRepo,'makeaccess.py'),'-o', 'mp3', '-i', thefile.assetName])
		else:
			print "makebroadcast cannot process the file specified"
			print "allowable filetypes are:"
			print aexts
	###THINGISDONE###

if __name__ == '__main__':
	main()
