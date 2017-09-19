import os
import imp

###INIT VARS###
#dn, fn = os.path.split(os.path.abspath(__file__))
dn = "S:/avlab/microservices"
global conf
rawconfig = imp.load_source('config',os.path.join(dn,'config.py'))
conf = rawconfig.config()
global ut
ut = imp.load_source("util",os.path.join(dn,"util.py"))
global log
log = imp.load_source('log',os.path.join(dn,'logger.py'))
global mtd
mtd = imp.load_source('mtd',os.path.join(dn,'makemetadata.py'))
global ff
ff = imp.load_source('ff',os.path.join(dn,'ffmpeg-stuff.py'))

args = {}
args = ut.dotdict(args)
args.so = "0b70bd7b-eaee-4819-beb8-995a0ea996ad3"
args.face = "fCD"
args.channelConfig = '1/4-inch Full Track Mono'
#args.channelConfig = '1/4-inch Half Track Stereo'
#args.channelConfig = '1/4-inch Quarter Track Stereo'
#args.channelConfig = '1/4-inch 4 Track'
args.aNumber = 'a19260'
ffproc = ff.audio_init_ffproc(conf.magneticTape.cnxn,**args)
full_ffstr = ff.prefix(args.so + "." + conf.ffmpeg.acodec_master_format) + ffproc.ff_suffix
print full_ffstr
print ""
print ffproc
print ""
if not "Stereo" in args.channelConfig:
	if ffproc.filename0:
		args.filename = ffproc.filename0
		full_ffstr = ff.prefix("cusb-a19260Ca.wav") + ' ' + ff.audio_secondary_ffproc(**args)
		print full_ffstr
	if ffproc.filename1:
		args.filename = ffproc.filename1
		full_ffstr = ff.prefix("cusb-a19260Da.wav") + ' ' + ff.audio_secondary_ffproc(**args)
		print full_ffstr