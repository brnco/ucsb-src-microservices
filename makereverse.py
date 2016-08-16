#reverser

import subprocess
import re
import argparse
import sys
import os

parser = argparse.ArgumentParser(description="slices, reverses input file, concatenates back together")
parser.add_argument('startObj',nargs ='?',help='the file to be reversed',)
args = vars(parser.parse_args())
endObj = os.path.basename(args['startObj'])
endObj,ext = os.path.splitext(endObj)
print endObj
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
		subprocess.call("ffmpeg -i " + args['startObj'] + " -ss " + str(count) + " -t 600 -acodec pcm_s24le concat" + str(count) + ".wav") #can't stream copy because of -af
		concat.write("file concat" + str(count) + ".wav\n") #write it with a newline
		count = count + 300 #incrase seconds by 300 (10min)
	concat.close() #housekeeping

	#concatenate the revsered output from slicer loop
	subprocess.call("ffmpeg -f concat -i concat.txt -c:a copy " + endObj + "-reversed.wav")
	returncode = 0
except:
	returncode = 1
	
if returncode == 0:	
	for f in os.listdir(os.getcwd()):
		if f.startswith("concat"):
			os.remove(f)
		elif os.path.exists(endObj + "-reversed.wav"):
			os.remove(args['startObj'])
else:
	print "Buddy, there was a problem reversing that file"