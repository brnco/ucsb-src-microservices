'''
qct-parse capps vhs
'''
import os
import sys
import subprocess
sys.path.insert(0,"S:/avlab/microservices")
import util as ut

def main():
    drive = "R:/Visual/avlab/new_ingest"
    txtfile = open("S:/avlab/microservices/utility-scripts/srcdig004-qct-parse.txt","a")
    for dirs, subdirs, files in os.walk(drive):
        for s in subdirs:
            if s.startswith("System"):
                continue
            sfullpath = os.path.join(dirs, s)
            with ut.cd(sfullpath):
                for f in os.listdir(os.getcwd()):
                    if f.endswith(".qctools.xml.gz"):
                        print os.path.join(os.getcwd(),f)
                        output = subprocess.check_output("python S:/avlab/qct-parse/qct-parse/qct-parse.py -p default8bit -i " + os.path.join(os.getcwd(),f),shell=True)
                        txtfile.write(output)
main()
