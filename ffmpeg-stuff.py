import os
import imp

def makeffstr_ftm():
	#generates an ffmpeg string for full-track mono captures
	return
def makeffstr_mono():
	#generates ffmpeg string for half- and quarter-track mono captures
	return
def	makeffstr_stereo():
	#generates ffmpeg string for stereo captures
	return
def reverse():
	#checks if a file needs to be reversed
	return
def sampleratenormalize():
	#checks if a file needs to have its sample rate converted to 96kHz
	return
def makebroadcast_audio():
	#makes an ffmpeg string to make a broadcast master for given audio file and params
	#basically copy lines 57-106 of mbc
	return
def makemp3():
	#makes an ffmpeg string to make an mp3 from the input file
	return

###INIT VARS###
dn, fn = os.path.split(os.path.abspath(__file__))
global conf
rawconfig = imp.load_source('config',os.path.join(dn,'config.py'))
conf = rawconfig.config()
global ut
ut = imp.load_source("util",os.path.join(dn,"util.py"))
global log
log = imp.load_source('log',os.path.join(dn,'logger.py'))
global mtd
mtd = imp.load_source('mtd',os.path.join(dn,'makemetadata.py'))

print conf.ffmpeg