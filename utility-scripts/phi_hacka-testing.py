import pyodbc
import sys
sys.path.insert(0,"S:/avlab/microservices")
###UCSB modules###
import config as rawconfig
import util as ut
from logger import log
import mtd
import makestartobject as makeso

def check_captured_FM(args, kwargs):
	sqlstr = """insert into
			table(field)
			values (select key from table where filename='""" + args.input + "'), '1')"""
	mtd.insertFM(sqlstr, pyodbc.connect(conf.NationalJukebox.cnxn))

def main():
    global conf
    conf = rawconfig.config()
    args = ut.dotdict({"input":sys.argv[0]})
    kwargs = {}
    check_captured_FM(args, kwargs)

main()
