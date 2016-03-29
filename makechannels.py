#takes args for input file(s)
#if 1 input file: splits to two stereo files
#if two input files, combines to 1 stereo file

import os
import subprocess
import argparse

def main():
	parser = argparse.ArgumentParser(description="Channel manipulation for AVLab items")
	parser.add_argument('-i1',help='input for the first file/ left stereo side/ channel 1/ side A')
	parser.add_argument('-i2',help='input for the second file/ right stereo side/ channel 2/ side B')
	args = vars(parser.parse_args())
	print args['i1']
	print args['i2']
	if args['i2'] == None:
		print "Split stereo to mono"
	else:
		print "Combine mono channels to stereo"
		fnamext = os.path.basename(os.path.abspath(args['i1']))
		fname, ext = os.path.splitext(fnamext)
		aNum = fname[:-2]
		endObj = os.path.join(os.path.dirname(args['i1']),aNum + 'a' + ext)
		subprocess.call(['ffmpeg','-i',args['i1'],'-i',args['i2'],'-filter_complex','[0:a][1:a]amerge=inputs=2[aout]','-map','[aout]',endObj])
	return

main()