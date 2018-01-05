#!/usr/bin/env python

import os
import subprocess
import argparse
import re
import time
import shutil
import sys
sys.path.insert(0,"S:/avlab/microservices")
#remove ^ in production
###UCSB modules###
import config as rawconfig
conf = rawconfig.config()
import util as ut
import logger as log
import mtd
import makestartobject as makeso

'''def main():
	drive = "E:/"
	for dirs, subdirs, files in os.walk(drive):
		for s in subdirs:
			endDir = os.path.join(drive, s)
			startDir = os.path.join(conf.video.repo, s[1]+"000", s)
			acc = "cusb-" + s + "-acc.mp4"
			qctools = "cusb-" + s + "-pres.mxf.qctools.xml.gz"
			pbcore = "cusb-" + s + "-pres.mxf.PBCore2.xml"
			print endDir
			if not os.path.exists(os.path.join(endDir, acc)) and os.path.exists(os.path.join(startDir, acc)):
				subprocess.call([conf.python, os.path.join(conf.scriptRepo, "hashmove.py"), "-c", os.path.join(startDir, acc), endDir])
			if not os.path.exists(os.path.join(endDir, qctools)) and os.path.exists(os.path.join(startDir, qctools)):
				subprocess.call([conf.python, os.path.join(conf.scriptRepo, "hashmove.py"), "-c", os.path.join(startDir, qctools), endDir])
			if not os.path.exists(os.path.join(endDir, pbcore)) and os.path.exists(os.path.join(startDir, pbcore)):
				subprocess.call([conf.python, os.path.join(conf.scriptRepo, "hashmove.py"), "-c", os.path.join(startDir, pbcore), endDir])
			print ""'''
def main():
	'''
	rename ucsb to cusb in preingestqc
	'''
	'''mdir = "R:/78rpm/avlab/new_ingest/audio_captures/master-sides"
	bdir = "R:/78rpm/avlab/new_ingest/audio_captures/broadcast-sides"
	qcdir = "R:/78rpm/avlab/new_ingest/pre-ingest-qc"
	for dirs, subdirs, files in os.walk(mdir):
		for f in files:
			if os.path.exists(os.path.join(bdir, f)):
				if os.path.exists(os.path.join(qcdir,f.replace(".wav",""))):
					foo = raw_input("check on " + f.replace(".wav","") + " in the qcdir")
					os.rename(os.path.join(dirs, f), os.path.join(dirs,f.replace(".wav","a.wav")))
					shutil.move(os.path.join(dirs,f.replace(".wav","a.wav")), os.path.join(qcdir,f.replace(".wav","")))
					continue
				else:
					os.makedirs(os.path.join(qcdir,f.replace(".wav","")))
				os.rename(os.path.join(bdir, f), os.path.join(bdir, f.replace(".wav", "b.wav")))
				shutil.move(os.path.join(bdir, f.replace(".wav", "b.wav")), os.path.join(qcdir,f.replace(".wav","")))
				os.rename(os.path.join(mdir, f), os.path.join(mdir, f.replace(".wav", "a.wav")))
				shutil.move(os.path.join(mdir, f.replace(".wav", "a.wav")), os.path.join(qcdir,f.replace(".wav","")))'''


if __name__ == '__main__':
	main()
