#!/usr/bin/env python
#avlab-magneticTape

import ConfigParser
import argparse
import getpass
import os
import subprocess
import csv
import re
import ast
import time
from distutils import spawn

#check that we have the required software to run this script
def dependencies():
	depends = ['bwfmetaedit','ffmpeg','ffprobe']
	for d in depends:
		if spawn.find_executable(d) is None:
			print "Buddy, you gotta install " + d
			sys.exit()
	return

#Context manager for changing the current working directory
class cd:
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

	
def deletebs(captureDir):
	for dirs,subdirs,files in os.walk(captureDir):
		for f in files:
			if f.endswith(".gpk") or f.endswith(".mrk") or f.endswith(".bak"):
				os.remove(os.path.join(captureDir,f))
	return


#hashmove processing folder to the repo	
def move(rawfname,aNumber,captureDir,mmrepo,archRepoDir):
	if aNumber.endswith("A") or aNumber.endswith("B") or aNumber.endswith("C") or aNumber.endswith("D"):
		aNumber = aNumber[:-1]
	dirNumber = aNumber
	processingDir = os.path.join(captureDir,dirNumber)
	if os.path.isdir(processingDir):
		endDirThousand = aNumber.replace("a","") #input arg here is a1234 but we want just the number
		#the following separates out the first digit and assigns an appropriate number of zeroes to match our dir structure
		if len(endDirThousand) < 5:
			endDirThousand = endDirThousand[:1] + "000"
		else:
			endDirThousand = endDirThousand[:2] + "000"
		endDir = os.path.join(archRepoDir,endDirThousand,dirNumber)
		#hashmove it and grip the output so we can delete the raw files YEAHHH BOY
		output = subprocess.Popen(['python',os.path.join(mmrepo,'hashmove.py'),processingDir,endDir],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		foo,err = output.communicate()
		print foo
		sourcehash = re.search('srce\s\S+\s\w{32}',foo)
		desthash = re.search('dest\s\S+\s\w{32}',foo)
		dh = desthash.group()
		sh = sourcehash.group()
		bexttxt = os.path.join("R:/audio/avlab/fm-exports/bexttxts","cusb-" + dirNumber + "-bext.txt")
		startObj1 = os.path.join("R:/audio/avlab/fm-exports/to_process",rawfname + ".txt")
		if sh[-32:] == dh[-32:]:
			os.remove(os.path.join(captureDir,rawfname + ".wav"))
			if os.path.exists(bexttxt): #can't give os.remove a file object it's gotta be a string grrrrr
				os.remove(os.path.join("R:/audio/avlab/fm-exports/bexttxts","cusb-" + dirNumber + "-bext.txt"))
			if os.path.exists(startObj1):
				os.remove(os.path.join("R:/audio/avlab/fm-exports/to_process",rawfname + ".txt"))
	return

def makefullffstr(ffstring,face,aNumber,channelConfig,processDir,rawfile):
	fullffstr = "ffmpeg -i " + rawfile + " " + ffstring
	endfileface = ''
	if face == "fAB" and "Quarter Track Stereo" in channelConfig:
		endfileface = "A"
	elif face == "fCD" and "Quarter Track Stereo" in channelConfig:
		endfileface = "C"
	elif face == "fAB" and "Half Track Stereo" in channelConfig or "Full Track Mono" in channelConfig or "Cassette" in channelConfig:
		endfileface = ""	
	else:
		endfileface = face.replace("f","")
	if  "AB" in face:
		fullffstr = fullffstr.replace("left",os.path.join(processDir,"cusb-" + aNumber + "Aa")).replace("right",os.path.join(processDir,"cusb-" + aNumber + "Ba"))
	elif "CD" in face:
		fullffstr = fullffstr.replace("left",os.path.join(processDir,"cusb-" + aNumber + "Ca")).replace("right",os.path.join(processDir,"cusb-" + aNumber + "Da"))
	fullffstr = fullffstr.replace("processed",os.path.join(processDir,"cusb-" + aNumber + endfileface + "a"))
	return fullffstr

	
def ffprocess(fullffstr,processDir):
	if not os.path.exists(processDir):
		os.makedirs(processDir)
	time.sleep(1)
	#do it
	with cd(processDir):
		try:
			output = subprocess.check_output(fullffstr,shell=True)
			returncode = 0
		except subprocess.CalledProcessError,e:
			output = e.output
			returncode = output
	return returncode

	
def reverse(rawfname,face,aNumber,channelConfig,processDir,mmrepo):
	revface = subprocess.check_output(["python","fm-stuff.py","-pi","-t","-p","reverse","-so",rawfname,"-f",face,"-cc",channelConfig])
	if "fA" in revface and not "fAB" in revface:
		if os.path.exists(os.path.join(processDir,"cusb-" + aNumber + "Aa.wav")):
			subprocess.check_output(['python',os.path.join(mmrepo,"makereverse.py"),os.path.join(processDir,"cusb-" + aNumber + "Aa.wav")])
	elif "fC" in revface and not "fCD" in revface:
		if os.path.exists(os.path.join(processDir,"cusb-" + aNumber + "Ca.wav")):	
			subprocess.check_output(['python',os.path.join(mmrepo,"makereverse.py"),os.path.join(processDir,"cusb-" + aNumber + "Ca.wav")])	
	elif "fB" in revface:
		if os.path.exists(os.path.join(processDir,"cusb-" + aNumber + "Ba.wav")):	
			subprocess.check_output(['python',os.path.join(mmrepo,"makereverse.py"),os.path.join(processDir,"cusb-" + aNumber + "Ba.wav")])
	elif "fD" in revface:
		if os.path.exists(os.path.join(processDir,"cusb-" + aNumber + "Da.wav")):	
			subprocess.check_output(['python',os.path.join(mmrepo,"makereverse.py"),os.path.join(processDir,"cusb-" + aNumber + "Da.wav")])
	elif "fAB" in revface:
		if os.path.exists(os.path.join(processDir,"cusb-" + aNumber + "Aa.wav")):
			subprocess.check_output(['python',os.path.join(mmrepo,"makereverse.py"),os.path.join(processDir,"cusb-" + aNumber + "Aa.wav")])
		elif os.path.exists(os.path.join(processDir,"cusb-" + aNumber + "a.wav")):
			subprocess.check_output(['python',os.path.join(mmrepo,"makereverse.py"),os.path.join(processDir,"cusb-" + aNumber + "a.wav")])
	elif "fCD" in revface:
		if os.path.exists(os.path.join(processDir,"cusb-" + aNumber + "Ca.wav")):
			subprocess.check_output(['python',os.path.join(mmrepo,"makereverse.py"),os.path.join(processDir,"cusb-" + aNumber + "Ca.wav")])
	return

	
def sampleratenormalize(processDir):
	#ok so by now every file in the processing dir is the correct channel config & plays in correct direction BUT
	#we need to normalize to 96kHz
	with cd(processDir):
		for f in os.listdir(os.getcwd()): #for each file in the processing dir
			if f.endswith(".wav"):
				print "ffprobe and resample if necessary"
				output = subprocess.Popen("ffprobe -show_streams -of flat " + f,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
				ffdata,err = output.communicate()
				#grep the bit about the duiration, in seconds
				#for line in lines:
				match = ''
				sr = ''
				match = re.search(r".*sample_rate=.*",ffdata)
				if match:
					_sr = match.group().split('"')[1::2]
					sr = _sr[0]
				if not sr == "96000":
					output = subprocess.call("ffmpeg -i " + f + " -ar 96000 -c:a pcm_s24le " + f.replace(".wav","") + "-resampled.wav")
					if os.path.getsize(f.replace(".wav","") + "-resampled.wav") > 50000:
						os.remove(os.path.join(os.getcwd(),f))
						time.sleep(1)
						os.rename(f.replace(".wav","") + "-resampled.wav",f) 
					else:	
						return
	return

	
def makebext(aNumber,processDir):
	bextstr = subprocess.check_output("python fm-stuff.py -pi -t -p bext -so " + aNumber.capitalize())
	with cd(processDir):
		for f in os.listdir(os.getcwd()):
			if f.endswith(".wav"):
				subprocess.check_output("bwfmetaedit --in-core-remove " + f)
				print "embedding MD5 hash of data chunk..."
				subprocess.check_output("bwfmetaedit --MD5-Embed-Overwrite " + f)
				print "embedding BEXT chunk..."
				subprocess.check_output("bwfmetaedit " + bextstr + " " + f)
	return




	
def main():
	#initialize the stuff
	parser = argparse.ArgumentParser(description="slices, reverses input file, concatenates back together")
	parser.add_argument('-s',dest='s',action="store_true",default=False,help='single mode, for processing a single transfer')
	parser.add_argument('-so','--startObj',dest='so',help="the rawcapture file.wav to process")
	args = parser.parse_args()
	config = ConfigParser.ConfigParser()
	dn, fn = os.path.split(os.path.abspath(__file__)) #grip the path to the directory where ~this~ script is located
	config.read(os.path.join(dn,"microservices-config.ini"))
	captureDir = config.get('magneticTape','new_ingest')
	archRepoDir = config.get('magneticTape','repo')
	avlab = config.get('magneticTape','avlab')
	scratch = config.get('magneticTape','scratch')
	mmrepo = config.get('global','scriptRepo')
	
	#get rid of the crap
	#deletebs(captureDir)

	#single mode check
	if args.s is True:
		file = args.so
		rawfname,ext = os.path.splitext(file)
		output = subprocess.check_output(["python","fm-stuff.py","-pi","-t","-p","nameFormat","-so",rawfname])
		processList = ast.literal_eval(output)
		if processList is not None:
			print processList
			face = processList[0]
			aNumber = "a" + processList[1]
			channelConfig = processList[2]
			ffstring = subprocess.check_output(["python","fm-stuff.py","-pi","-t","-p","ffstring","-so",rawfname,"-f",face,"-cc",channelConfig])
			if ffstring is not None:
				#init folder to do the work in
				processDir = os.path.join(captureDir,aNumber)
				#make the full ffstr using the paths we have
				fullffstr = makefullffstr(ffstring,face,aNumber,channelConfig,processDir,os.path.join(captureDir,file))
				print fullffstr
				#run ffmpeg on the file and make sure it completes successfully
				returncode = ffprocess(fullffstr,processDir)
				if returncode == 0:
					#os.remove(os.path.join(captureDir,rawfname + ".wav"))
					print "foo"
				else:
					return
				returncode = 0
				#if we need to reverse do it
				#note here to add output checker for reverse
				reverse(rawfname,face,aNumber,channelConfig,processDir,mmrepo)
				#if we need to normalize our sample rate to 96kHz, because we sped up or slowed down a recording, do it here
				#note here to add output checker for reverse
				sampleratenormalize(processDir)
				#fill out the bext chunk
				makebext(aNumber,processDir)
	else:
		for dirs,subdirs,files in os.walk(captureDir):
			for file in files:
				if file.endswith(".gpk") or file.endswith(".mrk") or file.endswith(".bak") or file.endswith(".pkf"):
					try:
						os.remove(file)
					except:
						pass
				elif file.endswith(".wav"):
					print file
					processNone = 0
					rawfname,ext = os.path.splitext(file)
					output = subprocess.check_output(["python","fm-stuff.py","-pi","-t","-p","nameFormat","-so",rawfname])
					processList = ast.literal_eval(output)
					if processList is not None:
						for p in processList:
							if p is None:
								processNone = 1
						if processNone > 0:
							break
						print processList
						face = processList[0]
						aNumber = "a" + processList[1]
						channelConfig = processList[2]
						ffstring = subprocess.check_output(["python","fm-stuff.py","-pi","-t","-p","ffstring","-so",rawfname,"-f",face,"-cc",channelConfig])
						if ffstring is not None:
							#init folder to do the work in
							processDir = os.path.join(captureDir,aNumber)
							#make the full ffstr using the paths we have
							fullffstr = makefullffstr(ffstring,face,aNumber,channelConfig,processDir,os.path.join(dirs,file))
							print fullffstr
							#run ffmpeg on the file and make sure it completes successfully
							returncode = ffprocess(fullffstr,processDir)
							if returncode == 0:
								#os.remove(os.path.join(captureDir,rawfname + ".wav"))
								print "foo"
							else:
								break
							returncode = 0
							#if we need to reverse do it
							#note here to add output checker for reverse
							reverse(rawfname,face,aNumber,channelConfig,processDir,mmrepo)
							#if we need to normalize our sample rate to 96kHz, because we sped up or slowed down a recording, do it here
							#note here to add output checker for reverse
							sampleratenormalize(processDir)
							#fill out the bext chunk
							makebext(aNumber,processDir)
							
						
	'''

				#hashmove them to the repo dir
				move(rawfname,aNumber,captureDir,mmrepo,archRepoDir)'''
	return

dependencies()
main()
