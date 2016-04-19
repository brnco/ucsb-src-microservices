#takes args for input file(s)
#if 1 input file: splits to two stereo files
#if two input files, combines to 1 stereo file

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
	parser.add_argument('-i1',help='input for the first file/ left stereo side/ channel 1/ side A')
	parser.add_argument('-i2',help='input for the second file/ right stereo side/ channel 2/ side B')
	args = vars(parser.parse_args()) #create a dictionary instead of leaving args in NAMESPACE land
	args['i1'] = args['i1'].replace("\\",'/') #for the windows peeps
	args['i2'] = args['i2'].replace("\\",'/')
	if args['i2'] == None:
		print "Split stereo to mono"
	else:
		print "Combine mono channels to stereo"
		fnamext = os.path.basename(os.path.abspath(args['i1'])) #grab just filename + extension
		fname, ext = os.path.splitext(fnamext) #split that too
		aNum = fname[:-2] #lop off the use char and face char to get canonical name
		endObj = os.path.join(os.path.dirname(args['i1']),aNum + 'a' + ext) #put it all back together with new name for output file
		#you can look up this ffmpeg call here: https://trac.ffmpeg.org/wiki/AudioChannelManipulation
		subprocess.call(['ffmpeg','-i',args['i1'],'-i',args['i2'],'-filter_complex','[0:a][1:a]amerge=inputs=2[aout]','-map','[aout]',endObj])
	return

dependencies()
main()