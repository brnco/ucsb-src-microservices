'''
streams an audio file based on supplied anumber
'''
import subprocess
import argparse
###UCSB modules###
import config as rawconfig
import makestartobject as makeso

def main():
	'''
	do the thing
	'''
	global conf
	conf = rawconfig.config()
	parser = argparse.ArgumentParser(description="listen to a magnetic audiotape transfer")
	parser.add_argument('-i', '--input', dest='i', help="the aNumber that you want to listen to")
	#parser.add_argument('-m','--mode',dest='m',choices=["single","batch"],help='mode, process a single file or every file in capture directory')
	args = parser.parse_args()
	startObj = makeso.parse_input(args.i)
	subprocess.call("ffplay " + startObj.replace("\\", "/"),shell=True)

if __name__ == '__main__':
	main()
