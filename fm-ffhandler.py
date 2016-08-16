#ff-handler
#generates ffmpeg strings for avlab-audio

import ConfigParser
import argparse
import os
import csv
import re
import subprocess
def main():
	parser = argparse.ArgumentParser(description="generates ffmpegstring based on filemaker output")
	parser.add_argument('startObj',nargs ='?',help='the file to be transcoded',)
	parser.add_argument('-r','--reverse',action="store_true",default=False,help="auto-callback for reversing files")
	args = vars(parser.parse_args()) #create a dictionary instead of leaving args in NAMESPACE land
	config = ConfigParser.ConfigParser()
	dn, fn = os.path.split(os.path.abspath(__file__)) #grip the path to the directory where ~this~ script is located
	config.read(os.path.join(dn,"microservices-config.ini"))
	toProcessDir = config.get('magneticTape','to_process')
	captureDir = config.get('magneticTape','new_ingest')
	#with args.so as random num from wavlab
	#find txt file and open
	#parse for each function
	rawfname, wav = os.path.splitext(args['startObj'])
	txtinfo = os.path.join(toProcessDir,args['startObj'])
	startObj = os.path.join(captureDir,rawfname)
	endObj = ''
	#init our strings
	ffstr = ''
	endright = ''
	endleft = ''
	channel0 = ''
	channel1 = ''
	hlvstr0 = ''
	hlvstr1 = ''
	dblstr0 = ''
	dblstr1 = ''
	zerostr = ''
	onestr = ''
	dblstr01 = ''
	hlvstr01 = ''
	silencestr = " -af silenceremove=0:0:-50dB:-10:1:-50dB"
	
	with open(txtinfo) as arb:
		process = csv.reader(arb, delimiter=",") #use csv lib to read it line by line
		for x in process: #result is list
			endObj = os.path.join(captureDir,"a" + x[0],rawfname)
			#let's do this for half-track mono tapes
			if '1/4-inch Half Track Mono' in x:
				channel0 = "-map_channel 0.0.0"
				channel1 = "-map_channel 0.0.1"
				
				#check for delete
				match = re.search('del_fA',str(x))
				if match:
					channel0 = ''
				match = re.search('del_fC',str(x))
				if match:
					channel0 = ''
				match = re.search('del_fB',str(x))
				if match:
					channel1 = ''
				match = re.search('del_fD',str(x))
				if match:
					channel1 = ''
					
				#check for halfspeed
				if 'hlvspd_fA' in x:
					hlvstr0 = ',"asetrate=48000"'
				if 'hlvspd_fC' in x:
					hlvstr0 = ',"asetrate=48000"'
				if 'hlvspd_fB' in x:
					hlvstr1 = ',"asetrate=48000"'
				if 'hlvspd_fD' in x:
					hlvstr1 = ',"asetrate=48000"'
				
				#check for double speed
				if 'dblspd_fA' in x:
					dblstr0 = ', "asetrate=192000"'
				if 'dblspd_fC' in x:
					dblstr0 = ', "asetrate=192000"'
				if 'dblspd_fB' in x:
					dblstr1 = ', "asetrate=192000"'
				if 'dblspd_fD' in x:
					dblstr1 = ', "asetrate=192000"'
			
				#for left channel, stream 0
				if channel0:
					zerostr = channel0
					if revstr0:
						zerostr = zerostr + silencestr + revstr0
						if hlvstr0:
							zerostr = zerostr + hlvstr0
						if dblstr0:
							zerostr = zerostr + dblstr0
					elif hlvstr1:
						zerostr = zerostr + silencestr + hlvstr0
					elif dblstr1:
						zerostr = zerostr + silencestr + dblstr0
					zerostr = zerostr + " -acodec pcm_s24le " + endObj + "left.wav "
				#for right channel, stream 1
				if channel1:
					onestr = channel1
					if revstr1:
						onestr = onestr + silencestr + revstr1
						if hlvstr1:
							onestr = onestr + hlvstr1
						if dblstr1:
							onestr = onestr + dblstr1
					elif hlvstr1:
						onestr = onestr + silencestr + hlvstr1
					elif dblstr1:
						onestr = onestr + silencestr + dblstr1
					onestr = onestr + " -acodec pcm_s24le " + endObj + "right.wav "	
				#print ffstr
				ffstr = "ffmpeg -i " + startObj + ".wav " + zerostr + onestr
				return ffstr,revstr01
			if '1/4-inch Full Track Mono' in x:
				ffstr = "ffmpeg -i " + startObj + ".wav " + silencestr + " -ac 1 -acodec pcm_s24le " + endObj + "-downmix.wav"
				return ffstr,revstr01
			else:
				#hlvspd_fAB
				if 'hlvspd_fAB' in x:
					hlvstr01 = ',"asetrate=48000"'
				#hlvspd_fCD
				if 'hlvspd_fCD' in x:
					hlvstr01 = ',"asetrate=48000"'
				#dblspd_fAB
				if 'dblspd_fAB' in x:
					dblstr01 = ',"asetrate=192000"'
				#dblspd_fCD
				if 'dblspd_fAB' in x:
					dblstr01 = ',"asetrate=192000"'
				ffstr = "ffmpeg -i " + startObj + ".wav " + silencestr + hlvstr01 + dblstr01 + " -acodec pcm_s24le " + endObj + "-processed.wav"
				return ffstr, revstr01
	return

ffmpegstring,revstr01 = main()
print ffmpegstring