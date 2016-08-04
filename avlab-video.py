#for pres mxf wrapped j2k files
#qctoolsreport
#pbcore2
#framemd5
#send acc + presmtd to R:\Visual\[0000]

import os
import subprocess
import sys
import glob
import ConfigParser
from distutils import spawn

#Context manager for changing the current working directory
class cd:
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

#find if we have the correct software installed		
def dependencies():
	depends = ['ffmpeg','ffprobe','MediaInfo','python']
	for d in depends:
		if spawn.find_executable(d) is None:
			print "Buddy, you gotta install " + d
			sys.exit()
	return


def main():
	dn, fn = os.path.split(os.path.abspath(__file__)) #grip the path to the directory where ~this~ script is located
	config.read(os.path.join(dn,"microservices-config.ini"))
	rootdir = config.get('video','new_ingest')
	for subdir, dirs, files in os.walk(rootdir):
		#cd into subdirs
		with cd(subdir):
			#pwd
			foo = os.getcwd()
			print foo
			#grab the mxf archival master file
			for presfile in glob.glob('*.mxf'):
				#instantiate var names of our output files
				_qctfile = presfile + '.qctools.xml.gz'
				_pbc2file = presfile + '.PBCore2.xml'
				_framemd5 = presfile + '.framemd5'
				#if there's not a qctools doc for it, make one
				if not os.path.exists(_qctfile):
					print _qctfile
					subprocess.call(['python','S:/avlab/microservices/makeqctoolsreport.py',presfile])
				#if there's not a PBCore2 doc for it, make one
				if not os.path.exists(_pbc2file):
					print _pbc2file
					#gotta give the PBCore2 filename as concat string here, _pbc2file is a file object
					subprocess.call(['MediaInfo','--Output=PBCore2','--LogFile=' + presfile + '.PBCore2.xml',presfile])
				#if there's not a framemd5 for it, make one
				if not os.path.exists(_framemd5):
					print _framemd5
					#gotta give the framemd5 filename as concat string here, _framemd5 is a file object
					subprocess.call(['ffmpeg','-i',presfile,'-f','framemd5',presfile + '.framemd5'])
	return

dependencies()
main()