import os
import subprocess
import argparse
import imp
###UCSB modules###
import config as rawconfig
import util as ut
import logger as log
import mtd
import makestartobject as makeso

def main():
	global conf
	conf = rawconfig.config()
	parser = argparse.ArgumentParser(description="listen to a magnetic audiotape transfer")
	parser.add_argument('-i','--input',dest='i',help="the aNumber that you want to listen to")
	#parser.add_argument('-m','--mode',dest='m',choices=["single","batch"],help='mode, process a single file or every file in capture directory')
	args = parser.parse_args()
	startObj = subprocess.check_output([conf.python,os.path.join(conf.scriptRepo,"makestartobject.py"),"-i",args.i])
	subprocess.call("ffplay " + startObj.replace("\\","/"),shell=True)

if __name__ == '__main__':	
	main()