#!/usr/bin/env python
#reverser

import subprocess
import re
import argparse
import sys
import os
import imp
from distutils import spawn

#check that we have required software installed
def dependencies():
	depends = ['ffmpeg','ffprobe']
	for d in depends:
		if spawn.find_executable(d) is None:
			print "Buddy, you gotta install " + d
			sys.exit()
	return
	
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
	log.log("started")
	parser = argparse.ArgumentParser(description="slices, reverses input file, concatenates back together")
	parser.add_argument('-so','--startObj',dest='so',help='the full path to the file to be reversed',)
	args = parser.parse_args()
	endObj = os.path.basename(args.so)
	endObj,ext = os.path.splitext(endObj)
	workingDir = os.path.dirname(args.so)
	###END INIT###
	with ut.cd(workingDir):
		#ffprobe input file and find duraiton
		output = subprocess.Popen(['ffprobe','-show_streams','-of','flat',args.so],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		ffdata,err = output.communicate()
		match = re.search(r".*duration=.*",ffdata) #get just the bit after duration
		if match:
			_dur = match.group().split('"')[1::2]
			dur = _dur[0] #separate out single value from list _dur

		#build a loop to slice and reverse audio, print fnames to txt to concat later	
		###init###
		count = 0 #init count
		returncode = 0 #init returncode to check for errors, if we don't, we could delete original transfer by mistake
		concat = open("concat.txt","wb") #init txt file that ffmpeg will parse later
		###end init###
		try:
			while (count < float(dur)): #loop through the file 300s at a time until u get to the end
				ffmpegstring = "ffmpeg -i " + args.so + " -ss " + str(count) + " -t 300 -af areverse -acodec pcm_s24le -threads 0 " + os.path.join(workingDir,"concat" + str(count) + ".wav")
				output = subprocess.check_output(ffmpegstring,shell=True) #can't stream copy because of -af
				concat.write("file concat" + str(count) + ".wav\n") #write it with a newline
				count = count + 300 #incrase seconds by 300 (10min)
			concat.close() #housekeeping
			returncode = 0
		except subprocess.CalledProcessError,e:
			output = e.output
			returncode = output
		foo = raw_input("eh")	
		#concatenate the revsered output from slicer loop
		ffmpegstring = "ffmpeg -f concat -i concat.txt -c:a copy -threads 0 " + endObj + "-reversed.wav"
		output = subprocess.call(ffmpegstring)
		###DELETE STUFF###
		if returncode == 0:	
			for f in os.listdir(os.getcwd()):
				print f
				match = ''
				match = re.match("concat",f)
				if match:
					os.remove(f)
			if os.path.exists(endObj + "-reversed.wav"):
				if os.path.getsize(endObj.replace(".wav","") + "-reversed.wav") > 50000: #validate that the reversed file is actually good and ok
					if os.path.exists(args.so):
						os.remove(args.so)
						os.rename(endObj + "-reversed.wav", args.so)
		else:
			print "Buddy, there was a problem reversing that file"

dependencies()	
main()