'''
avlab-discs
post-capture-processing for grooved disc materials
'''
import os
import subprocess
import argparse
###UCSB modules###
import config as rawconfig
import util as ut
import logger as log

def main():
	'''
	do the thing
	'''
	#initialize the stuff
	conf = rawconfig.config()
	parser = argparse.ArgumentParser(description="processes non-PHI disc transfers")
	parser.add_argument('-m', dest='m', choices=['batch', 'single'], default=False, help='mode, for processing a single transfer or a bacth in new_ingest')
	parser.add_argument('-i', '--input', dest='i', help="the rawcapture file.wav to process, single mode only")
	args = parser.parse_args()
	captureDir = conf.discs.rawArchDir
	archRepoDir = conf.discs.archRepoDir
	bextsDir = conf.discs.mtdCaptures
	for _, subdirs, files in os.walk(captureDir):
		for f in files:
			if f.endswith(".gpk"):
				with ut.cd(os.pardir(f)):
					os.remove(f)
		for s in subdirs:
			with ut.cd(os.path.join(captureDir, s)):
				endObj1 = s + "b.wav"
				if os.path.isfile(s + "b.wav"):
					subprocess.call(['python', os.path.join(conf.scriptRepo, "makebroadcast.py"), '-ff', endObj1])
					os.remove(endObj1)
					os.rename(s + "c.wav", endObj1)
				if os.path.isfile(s + "a.wav"):
					subprocess.call(['bwfmetaedit', '--Originator=US, CUSB, SRC', '--OriginatorReference=' + s, '--MD5-Embed-Overwrite', s + "a.wav"])
			subprocess.call(['python', os.path.join(conf.scriptRepo, "hashmove.py"), os.path.join(captureDir, s), os.path.join(archRepoDir, s)])
	return

if __name__ == "__main__":
	main()