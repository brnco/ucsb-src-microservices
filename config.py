'''
sets configuration dictionary for pathnames and ffmpeg options using microservices-config.ini
'''
import ConfigParser
import os
###UCSB modules###
import util as ut

def config():
	'''
	do the thing
	'''
	scriptRepo, fn = os.path.split(os.path.abspath(__file__))
	config = ConfigParser.RawConfigParser(allow_no_value=True)
	config.read(os.path.join(scriptRepo, "microservices-config.ini"))
	conf = {'log':{}, 'NationalJukebox':{}, 'cylinders':{}, 'discs':{}, 'video':{}, 'magneticTape':{}}
	tags = ['location', 'AudioArchDir', 'AudioBroadDir', 'PreIngestQCDir',
			'VisualArchRawDir', 'BatchDir', 'scratch', 'new_ingest', 'repo',
			'avlab', 'lto_stage', 'vid_leads', 'master_format_policy', 'access_format_policy', 'ff_master_format_policy',
			'cnxn']
	for c in conf:
		for t in tags:
			try: #see if it's in the config section
				if not t == 'cnxn':
					conf[c][t] = ut.drivematch(config.get(c, t)) #if it is, replace _ necessary for config file with . which xml attributes use, assign the value in config
				else:
					conf[c][t]=config.get(c, t)
			except: #if no config tag exists, do nothing so we can move faster
				pass
		conf[c] = ut.dotdict(conf[c])
	ff = {}
	tags = ['filter_silence', 'filter_halfspeed', 'filter_doublespeed',
			'filter_loudnorm', 'filter_afade', 'filter_deinterlace',
			'acodec_master', 'acodec_master_format',
			'acodec_master_arate', 'acodec_master_writebext', 'acodec_broadcast_format',
			'acodec_broadcast', 'acodec_broadcast_rate', 'acodec_access_format',
			'acodec_access_arate', 'acodec_access_bitrate', 'acodec_writeid3',
			'vcodec_master', 'vcodec_master_pixel_format', 'vcodec_master_dimensions',
			'vcodec_master_vrate', 'vcodec_master_acodec', 'vcodec_master_arate',
			'vcodec_broadcast', 'vcodec_master_format', 'vcodec_broadcast_pixel_format',
			'vcodec_broadcast_acodec', 'vcodec_broadcast_arate', 'vcodec_broadcast_format',
			'vcodec_broadcast_dimensions', 'vcodec_broadcast_vrate', 'vcodec_broadcast_bitrate']
	for t in tags:
		try:
			ff[t] = config.get("ffmpeg", t)
		except:
			pass
	conf['ffmpeg'] = ut.dotdict(ff)
	conf['scriptRepo'] = scriptRepo
	conf['python'] = ut.pythonpath()
	conf = ut.dotdict(conf)
	return conf
