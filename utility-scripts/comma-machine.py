'''
inserts a space after a comma
'''
import os
import subprocess
import argparse
import re
import time
import sys
sys.path.insert(0,"S:/avlab/microservices")
#remove ^ in production
###UCSB modules###
import config as rawconfig
import util as ut
import logger as log
import mtd
import makestartobject as makeso

def main():
	'''
	do the thing
	'''
	with open("S:/avlab/microservices/" + sys.argv[1].replace(".py","-cm.py"), "w") as nf:
		with open("S:/avlab/microservices/" + sys.argv[1]) as of:
			for line in of:
				sub = re.sub(r'(,)(\S)',r'\1 \2',line)
				nf.write(sub.encode('utf-8'))
	
if __name__ == '__main__':
	main()