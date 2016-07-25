#takes args for input file(s)
#if 1 input file: splits to two stereo files
#if two input files, combines to 1 stereo file
#you can look up this ffmpeg calls here: https://trac.ffmpeg.org/wiki/AudioChannelManipulation

import os
import subprocess
import argparse
import sys
from distutils import spawn

#check that we have the required software to run this script
def dependencies():
	depends = ['ffmpeg']
	for d in depends:
		if spawn.find_executable(d) is None:
			print "Buddy, you gotta install " + d
			sys.exit()
	return

def main():
	#initialize arguments using argparse
	parser = argparse.ArgumentParser(description="Channel manipulation for AVLab items")
	parser.add_argument('-so','--startObj',dest='so',nargs ='+',help='the file(s) to be transcoded',)
	parser.add_argument('-r','--reverse',dest='r',help='which tape face to reverse, if necessary',)
	parser.add_argument('-d','--delete',dest='d',help='which tape face to delete, if necessary',)
	#parser.add_argument('-del','--delete',dest='del',choices=[1,2],help='the file(s) to be transcoded',)
	args = parser.parse_args()#create a dictionary instead of leaving args in NAMESPACE land
	
	if len(args.so) == 1:
		print "split stereo to mono"
		i2 = "foo"
		for s in args.so:
			if s.endswith("Ca.wav"):
				blah = s
				blah = blah.replace("Ca.wav","Ea.wav")
				os.rename(s,blah)
				i1 = blah
				endright = os.path.basename(os.path.abspath(s))
				endright = endright.replace("Ca.wav","Da.wav")
				endleft = os.path.basename(os.path.abspath(s))
				endleft = endleft.replace("Ea.wav","Ca.wav")
			elif s.endswith("a.wav"):
				endright = os.path.basename(os.path.abspath(s))
				endright = endright.replace("a.wav","Ba.wav")
				endleft = os.path.basename(os.path.abspath(s))
				endleft = endleft.replace("a.wav","Aa.wav")
		ffmpegstring = "ffmpeg -i " + i1 + " -map_channel 0.0.0 " + " -acodec pcm_s24le " + endleft + " -map_channel 0.0.1 " + " -acodec pcm_s24le " + endright

	elif len(args.so) == 2:
		print "combine multi monos to stereo"
		for s in args.so:
			if s.endswith("Aa.wav"):
				i1 = s
				endObj = s.replace("Aa.wav","a.wav")
			if s.endswith("Ba.wav"):
				i2 = s
				
		ffmpegstring = "ffmpeg -i " + i1 + " -i " + i2 + ' -filter_complex "[0:a][1:a]amerge=inputs=2[aout]" -map "[aout]" -acodec pcm_s24le ' + endObj
		
	else:
		print "Buddy, your inputs are outta range"
		print "Type 'python changechannels.py -h' for more info"
		sys.exit()
	
	subprocess.call(ffmpegstring) #actually do the thing
	
	#delete the inputs because we dont need em
	if os.path.exists(i1):
		os.remove(i1)
	if os.path.exists(i2):
		os.remove(i2)
	return

dependencies()
main()