import os
import subprocess
import argparse
import imp

def main():
	dn, fn = os.path.split(os.path.abspath(__file__))
	global conf
	rawconfig = imp.load_source('config',os.path.join(dn,'config.py'))
	conf = rawconfig.config()
	global ut
	ut = imp.load_source("util",os.path.join(dn,"util.py"))
	global log
	log = imp.load_source('log',os.path.join(dn,'logger.py'))
	parser = argparse.ArgumentParser(description="listen to an audio transfer")
	parser.add_argument('-i','--startObj',dest='i',help="the aNumber that you want to listen to")
	#parser.add_argument('-m','--mode',dest='m',choices=["single","batch"],help='mode, process a single file or every file in capture directory')
	args = parser.parse_args()
	startObj = subprocess.check_output([conf.python,os.path.join(conf.scriptRepo,"makestartobject.py"),"-i",args.i])
	subprocess.call("ffplay " + startObj.replace("\\","/"),shell=True)
	
main()
