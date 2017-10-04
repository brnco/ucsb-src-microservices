#!/usr/bin/env python
#reverser

import subprocess
import re
import argparse
import sys
import os
###UCSB modules###
import config as rawconfig
import util as ut
import logger as log
import mtd
import makestartobject as makeso

def process(args):
	count = 0 #init count
	concat = open("concat.txt","w") #init txt file that ffmpeg will parse later	
	try:
		while (count < float(args.dur)): #loop through the file 300s at a time until u get to the end
			ffmpegstring = "ffmpeg -i " + args.i + " -ss " + str(count) + " -t 300 -af areverse -acodec pcm_s24le -threads 0 " + os.path.join(args.workingDir,"concat" + str(count) + ".wav")
			output = subprocess.check_output(ffmpegstring)
			concat.write("file concat" + str(count) + ".wav\n") #write it with a newline
			count = count + 300 #incrase seconds by 300 (5min)
		concat.close() #housekeeping
		rtncode = True
	except subprocess.CalledProcessError,e:
		output = e.output
		rtncode = output
	return rtncode
	
def process_short(args):
	ffmpegstring = "ffmpeg -i " + args.i + " -af areverse -c:a pcm_s24le " + args.i.replace(".wav","-reversed.wav")
	try:
		output = subprocess.check_output(ffmpegstring) #can't stream copy because of -af
		rtncode = True
	except subprocess.CalledProcessError,e:
		rtncode = e.returncode
	return rtncode
	
def main():
	###INIT VARS###
	global conf
	conf = rawconfig.config()
	log.log("started")
	parser = argparse.ArgumentParser(description="slices, reverses input file, concatenates back together")
	parser.add_argument('-i','--input',dest='i',help='the full path to the file to be reversed',)
	args = parser.parse_args()
	endObj = os.path.basename(args.i)
	endObj,ext = os.path.splitext(endObj)
	workingDir = args.workingDir = os.path.dirname(args.i)
	###END INIT###
	with ut.cd(workingDir):
		#ffprobe input file and find duraiton
		output = subprocess.Popen(['ffprobe','-show_streams','-of','flat',args.i],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		ffdata,err = output.communicate()
		match = re.search(r".*duration=.*",ffdata) #get just the bit after duration
		if match:
			_dur = match.group().split('"')[1::2]
			dur = args.dur = _dur[0] #separate out single value from list _dur
		###end init###
		if float(dur) <= 300.0:
			revWorked = process_short(args)	
		else:
			revWorked = process(args)
			#concatenate the revsered output from slicer loop
			if revWorked is True:	
				ffmpegstring = "ffmpeg -f concat -i concat.txt -c:a copy -threads 0 " + endObj + "-reversed.wav"
				try:
					output = subprocess.call(ffmpegstring)
					revWorked = True
				except subprocess.CalledProcessError,e:
					revWorked = e.returncode
		###DELETE STUFF###
		if revWorked is True:	
			for f in os.listdir(os.getcwd()):
				match = ''
				match = re.match("concat",f)
				if match:
					os.remove(f)
			if os.path.exists(endObj + "-reversed.wav"):
				if os.path.getsize(endObj.replace(".wav","") + "-reversed.wav") > 50000: #validate that the reversed file is actually good and ok
					if os.path.exists(args.i):
						os.remove(args.i)
						os.rename(endObj + "-reversed.wav", args.i)
		else:
			print "Buddy, there was a problem reversing that file"
if __name__ == '__main__':
	main()