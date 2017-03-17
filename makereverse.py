#!/usr/bin/env python
#reverser

import subprocess
import re
import argparse
import sys
import os
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
	
def main():
	parser = argparse.ArgumentParser(description="slices, reverses input file, concatenates back together")
	parser.add_argument('startObj',nargs ='?',help='the file to be reversed',)
	args = vars(parser.parse_args())
	endObj = os.path.basename(args['startObj'])
	endObj,ext = os.path.splitext(endObj)
	workingDir = os.path.dirname(args['startObj'])
	with cd(workingDir):
		#ffprobe input file
		output = subprocess.Popen(['ffprobe','-show_streams','-of','flat',args['startObj']],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		ffdata,err = output.communicate()

		#grep the bit about the duiration, in seconds
		match = re.search(r".*duration=.*",ffdata)
		if match:
			_dur = match.group().split('"')[1::2]
			dur = _dur[0] #separate out single value from list _dur

		#build a loop to slice and reverse audio, print fnames to txt	
		count = 0 #init count
		returncode = 0 #init returncode to check for errors, if we don't, we could delete original transfer by mistake
		concat = open("concat.txt","wb") #init txt file that ffmpeg will parse later

		try:
			while (count < float(dur)):
				ffmpegstring = "ffmpeg -i " + args['startObj'] + " -ss " + str(count) + " -t 600 -af areverse -acodec pcm_s24le " + os.path.join(workingDir,"concat" + str(count) + ".wav")
				output = subprocess.check_output(ffmpegstring,shell=True) #can't stream copy because of -af
				concat.write("file concat" + str(count) + ".wav\n") #write it with a newline
				count = count + 300 #incrase seconds by 300 (10min)
			concat.close() #housekeeping
			returncode = 0
		except subprocess.CalledProcessError,e:
			output = e.output
			returncode = output
			
		#concatenate the revsered output from slicer loop
		ffmpegstring = "ffmpeg -f concat -i concat.txt -c:a copy " + endObj + "-reversed.wav"
		output = subprocess.call(ffmpegstring)
		if returncode == 0:	
			for f in os.listdir(os.getcwd()):
				print f
				match = ''
				match = re.match("concat",f)
				if match:
					os.remove(f)
			if os.path.exists(endObj + "-reversed.wav"):
				print "in here"
				if os.path.getsize(endObj.replace(".wav","") + "-reversed.wav") > 50000:
					print "in here2"
					if os.path.exists(args['startObj']):
						print "inhere3"
						os.remove(args['startObj'])
						os.rename(endObj + "-reversed.wav", args['startObj'])
		else:
			print "Buddy, there was a problem reversing that file"
	return

dependencies()	
main()