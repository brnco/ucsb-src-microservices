import pyodbc
import sys
import os
import subprocess
sys.path.insert(0,"S:/avlab/microservices")
#sys.path.insert(0, "/Volumes/special/DeptShare/special/avlab/microservices")
###UCSB modules###
import config as rawconfig
import util as ut
from logger import log
import mtd
import makestartobject as makeso

def mark_captured_FM(args, kwargs):
	#sqlstr = """update SONYLOCALDIG set audioProcessed='1' where filename='""" + args.input + """'"""
	#mtd.insertFM(sqlstr, pyodbc.connect(conf.NationalJukebox.cnxn))
	mtd.insertFM("""update SONYLOCALDIG set capturedImage='1' where filename='""" + args.input + """'""", pyodbc.connect(conf.NationalJukebox.cnxn))
'''
table:field
SONYLOCALDIG:imageProcessed
SONYLOCALDIG:capturedImage
SONYLOCALDIG:audioProcessed
SONYLOCALDIG:readyToQC
'''

def main():
	global conf
	conf = rawconfig.config()
	#args = ut.dotdict({"input":sys.argv[1]})
	#cnxn = pyodbc.connect(conf.NationalJukebox.cnxn)
	for dirs, subdirs, files in os.walk(conf.NationalJukebox.PreIngestQCDir):
		for s in subdirs:
			#mtd.insertFM("""update SONYLOCALDIG set readyToQC='1' where filename='""" + s.replace("cusb_","ucsb_") + """'""", cnxn)
			print s
			subprocess.call([conf.python, os.path.join(conf.scriptRepo, "makesip.py"), "-m", "nj", "-i", s])
	#cnxn.close()

main()
