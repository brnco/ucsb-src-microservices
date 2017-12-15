'''
generates ffmpeg strings
runs ffmpeg and returns success or failure
'''
import os
import imp
import subprocess
import pyodbc
###UCSB modules###
import util as ut
import logger as log
import mtd
import makestartobject as makeso

def audio_init_ffproc(conf, kwargs):
	'''
	generates ffmpeg process data for magnetic tape transfers
	'''
	args = ut.dotdict(kwargs)
	cnxn = pyodbc.connect(conf.magneticTape.cnxn)
	ffproc = mtd.get_ff_processes(args, cnxn) #get faces/ processes from filemaker"
	ffproc = ut.dotdict(ffproc)
	print args.channelConfig
	if not "Stereo" in args.channelConfig and not "Cassette" in args.channelConfig:
		print "mono"
		###FOR MONO TAPES###
		channel0 = ut.dotdict({'map':"-map_channel 0.0.0"})
		channel1 = ut.dotdict({'map':"-map_channel 0.0.1"})
		for k, v in ffproc.iteritems():
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
		if ff_suffix0 and ff_suffix1:
			ff_suffix = ff_suffix0 + ' ' + ff_suffix1
		elif ff_suffix0:
			ff_suffix = ff_suffix0
		elif ff_suffix1:
			ff_suffix = ff_suffix1
		else:
			ff_suffix = None
		###END MONO###
	else:
		###FOR STEREO TAPES###
		channel0 = ut.dotdict({"silence":conf.ffmpeg.filter_silence, "af":'', "faceChar":''})
		if "Quarter" in args.channelConfig:
			channel0.faceChar = args.face[1]
		elif "Half" in args.channelConfig:
			channel0.faceChar = ''
		for k, v in ffproc.iteritems():
			if v is not None:
				if k == 'dblface':
					channel0.af = 'asetrate=192000'
				elif k == 'hlvface':
					channel0.af = 'asetrate=48000'
		ff_suffix0 = '-af ' + channel0.silence
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

def audio_secondary_ffproc(conf, kwargs):
	'''
		make a second ffmpeg string for mono files of magnetic tape transfers
		silenceremove works on the file level not stream level
		so, in order to do the heads and tails trims on mono files that were captured in stereo,
		we need to run them through ffmpeg again
	'''
	print kwargs
	ff_suffix = "-af " + conf.ffmpeg.filter_silence + " -c:a " + conf.ffmpeg.acodec_master + ' ' + kwargs['filename'].replace(".wav", "-silenced.wav")
	return ff_suffix

def prefix(obj):
	'''
	makes an ffmpeg prefix for supplied filepath
	'''
	ff_prefix = "ffmpeg -i " + obj + " "
	return ff_prefix

def sampleratenormalize(conf, kwargs):
	'''
	returns ff_str to normalize file's sample rate to 96kHz
	'''
	full_ffstr = prefix(kwargs.filename) + "-ar " + conf.ffmpeg.acodec_master_arate + " -c:a " + conf.ffmpeg.acodec_master + " " + kwargs.filename.replace(".wav", "-resampled.wav")
	return full_ffstr

def probe_streams(obj):
	'''
	returns dictionary with each stream element
	e.g. {"0.pix_fmt":"yuv420p10le"}
	'''
	streams = {}
	ffstr = "ffprobe -show_streams -of flat " + obj
	output = subprocess.Popen(ffstr, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	_out = output.communicate()
	out = _out[0].splitlines()
	for o in out:
		key, value = o.split("=")
		key = key.replace("streams.stream.","")
		streams[str(key)] = value.replace('"','')
	if streams:
		return streams
	else:
		print _out[1]
		return False

def go(ffstr):
	'''
	runs ffmpeg, returns true is success, error is fail
	'''
	try:
		if os.name == 'posix':
			returncode = subprocess.check_output(ffstr, shell=True)
		else:
			returncode = subprocess.check_output(ffstr)
		returncode = True
	except subprocess.CalledProcessError, e:
		returncode = e.returncode
		print returncode
	return returncode
