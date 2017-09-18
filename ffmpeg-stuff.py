import os
import imp
import pyodbc
import subprocess

def get_processes(args,cnxn):
	#gets faces/ processes from filemaker form filled out by digi techs
	processes = ['delface','hlvface','dblface','revface'] #list of processes
	ffproc = {}
	sqlstr = '''select 
				deleting_''' + args.face + ",halving_" + args.face + ",doubling_" + args.face + ",reversing_" + args.face + ''' 
				from Audio_Masters 
				where rawCaptureName_''' + args.face + "='" + args.so + """'
				or Audio_Masters.rawCaptureName_""" + args.face + "='" + args.so + ".wav'"
	result = mtd.queryFM_single(sqlstr,cnxn) #use makemetadata to ask filemaker for this info
	if result is not None:
		for index,r in enumerate(result):
			if r == 'None':
				r = None #transform fm output of string "None" to python type None
			ffproc[processes[index]] = r
	return ffproc
	
def audio_init_ffproc(cnxn,**kwargs):
	#generates ffmpeg process data
	args = ut.dotdict(kwargs)
	cnxn = pyodbc.connect(cnxn)
	ffproc = get_processes(args,cnxn) #get faces/ processes from filemaker"
	ffproc = ut.dotdict(ffproc)
	if not "Stereo" in args.channelConfig:
		###FOR MONO TAPES###
		channel0 = ut.dotdict({'map':"-map_channel 0.0.0"})
		channel1 = ut.dotdict({'map':"-map_channel 0.0.1"})
		for k,v in ffproc.iteritems():
			#convert fm outputs to ffmpeg strings
			if v is not None:
				if k == 'dblface' and (v == 'fA' or v == 'fC'):
					channel0.af = 'asetrate=192000'
				elif k == 'dblface' and (v == 'fB' or v == 'fD'):
					channel1.af = 'asetrate=192000'
				elif k == 'hlvface' and (v == 'fA' or v == 'fC'):
					channel0.af = 'asetrate=48000'
				elif k == 'hlvface' and (v == 'fB' or v == 'fD'):
					channel1.af = 'asetrate=48000'
				if k == 'delface' and (v == 'fA' or v == 'fC'):
					channel0 = {}
				elif k == 'delface' and (v == 'fB' or v == 'fD'):
					channel1 = {}
		ff_suffix0 = ff_suffix1 = ''
		#for the first face, if it exists
		if channel0:
			ff_suffix0 = channel0.map
			if channel0.af:
				ff_suffix0 = ff_suffix0 + ' -af ' + channel0.af
			###GENERATE FILENAME FOR FACE0###
			ffproc.filename0 = filename0 = "cusb-" + args.aNumber + args.face[1] + "a." + conf.ffmpeg.acodec_master_format
			ff_suffix0 = ff_suffix0 + ' -c:a ' + conf.ffmpeg.acodec_master + ' ' + filename0
		#for the second face, if it exists
		if channel1:
			ff_suffix1 = channel1.map
			if channel1.af:
				ff_suffix1 = ff_suffix1 + ' -af ' + channel1.af
			###GENERATE FILENAME FOR FACE1"""
			ffproc.filename1 = filename1 = "cusb-" + args.aNumber + args.face[2] + "a." + conf.ffmpeg.acodec_master_format
			ff_suffix1 = ff_suffix1 + ' -c:a ' + conf.ffmpeg.acodec_master + ' ' + filename1
		###PUT IT TOGETHER###
		ff_suffix = ff_suffix0 + ' ' + ff_suffix1
		###END MONO###
	else:
		###FOR STEREO TAPES###
		channel0 = ut.dotdict({"silence":conf.ffmpeg.filter_silence,"af":'',"faceChar":''})
		if "Quarter" in args.channelConfig:
			channel0.faceChar = args.face[1]
		elif "Half" in args.channelConfig:
			channel0.faceChar = ''
		for k,v in ffproc.iteritems():
			if v is not None:
				if k == 'dblface':
					channel0.af = 'asetrate=192000'
				elif k == 'hlvface':
					channel0.af = 'asetrate=48000'
		ff_suffix0 = ' -af ' + channel0.silence
		if channel0.af:
			ff_suffix0 = ff_suffix0 + ',' + channel0.af 
		ff_suffix0 = ff_suffix0 + ' -c:a ' + conf.ffmpeg.acodec_master
		###GENERATE FILENAME FOR THE OBJECT###
		ffproc.filename0 = filename0 = 'cusb-' + args.aNumber + channel0.faceChar + 'a.' + conf.ffmpeg.acodec_master_format	
		###PUT IT TOGETHER###
		ff_suffix = ff_suffix0 + ' ' + filename0
		###END STEREO###
	ffproc.ff_suffix = ff_suffix
	return ffproc

def audio_secondary_ffproc(**kwargs):
	'''
		make a second ffmpeg string for mono files
		silenceremove works on the file level not stream level
		so, in order to do the heads and tails trims on mono files that were captured in stereo,
		we need to run them through ffmpeg again
	'''
	args = ut.dotdict(kwargs)
	ff_suffix = "-af " + conf.ffmpeg.filter_silence + " -c:a " + conf.ffmpeg.acodec_master + ' ' + args.filename.replace(".wav","-silenced.wav")
	return ff_suffix
	
def prefix(obj):
	ff_prefix = "ffmpeg -i " + obj + " "
	return ff_prefix
	
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

def go(ffstr):
	try:
		returncode = subprocess.check_output(ffstr)
		returncode = 0
	except subprocess.CalledProcessError,e:
		returncode = e.returncode
	return returncode	
		

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