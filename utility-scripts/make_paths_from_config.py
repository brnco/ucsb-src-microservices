#!/usr/bin/env python

import os
import subprocess
import argparse
import re
import time
import sys
sys.path.insert(0,"/Volumes/thedata/developments/src-avlab-microservices")
sys.path.insert(0,"/Library/Python/2.7/site-packages")
#remove ^ in production
###UCSB modules###
import config as rawconfig
conf = rawconfig.config()
import util as ut
import logger as log
import mtd
import makestartobject as makeso

def main():
	tlds = ['log', 'NationalJukebox', 'cylinders', 'discs', 'video', 'magneticTape']
	for paths in tlds:
		for p in conf[paths]:
			if not conf[paths][p].startswith("DRIVER") and not conf[paths][p].endswith(".xml"):
				if not os.path.exists(conf[paths][p]):
					os.makedirs(conf[paths][p])
				'''except:
					print conf[paths][p]'''

if __name__ == '__main__':
	main()
