'''
loops through raw_ingest and find files unlinked to FM and also silent and deletes them
'''

#!/usr/bin/env python

import os
import subprocess
import argparse
import re
import time
import sys
import pyodbc
sys.path.insert(0,"S:/avlab/microservices")
#remove ^ in production
###UCSB modules###
import config as rawconfig
global conf
conf = rawconfig.config()
import util as ut
import logger as log
import mtd
import makestartobject as makeso

def inFM(thefile):
    acf = mtd.get_aNumber_channelConfig_face(conf.magneticTape.cnxn,**thefile)
    if acf is None:
        return False
    else:
        return True

def oldEnuf(thefile):
    now = time.time()
    thefile.createdDate = os.path.getctime(thefile.fullpath)
    if (now - thefile.createdDate) > (30*24*60*60):
        return True
    else:
        return False

def process(thefile):
    isinFM = inFM(thefile)
    if isinFM is False:
            print "not in FM"
            isoldEnuf = oldEnuf(thefile)
            if isoldEnuf is True:
                print "removed"
                os.remove(thefile.fullpath)
            else:
                print "not old enuf"
    else:
        print "is in FM"

def main():
    '''
    thefile = ut.dotdict({})
    thefile.fnamext = sys.argv[1]
    thefile.rawcapNumber, thefile.ext = os.path.splitext(thefile.fnamext)
    thefile.fullpath = os.path.join(conf.magneticTape.new_ingest, thefile.fnamext)
    '''
    for dirs, subdris, files in os.walk(conf.magneticTape.new_ingest):
        for f in files:
            thefile = ut.dotdict({})
            thefile.fnamext = f
            thefile.rawcapNumber, thefile.ext = os.path.splitext(f)
            thefile.fullpath = os.path.join(dirs, f)
            print thefile.fnamext
            if thefile.ext == '.gpk':
                try:
                    os.remove(thefile.fullpath)
                except:
                    continue
            else:
                process(thefile)
                print ""


if __name__ == '__main__':
	main()
