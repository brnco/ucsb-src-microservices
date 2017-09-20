#config
import ConfigParser
import os
import unittest
###UCSB modules###
import util as ut
import logger as log
import mtd
import makestartobject as makeso

def config():
	scriptRepo, fn = os.path.split(os.path.abspath(__file__))
	config = ConfigParser.RawConfigParser(allow_no_value=True)
	config.read(os.path.join(scriptRepo,"microservices-config.ini"))
	conf = {'log':{},'NationalJukebox':{},'cylinders':{},'discs':{},'video':{},'magneticTape':{}}
	tags = ['location','AudioArchDir','AudioBroadDir','PreIngestQCDir',
			'VisualArchRawDir','BatchDir','scratch','new_ingest','repo',
			'avlab','lto_stage','vid_leads','master_format_policy','access_format_policy','ff_master_format_policy',
			'cnxn']
	for c in conf:
		for t in tags:
			try: #see if it's in the config section
				if not t == 'cnxn':
					conf[c][t] = ut.drivematch(config.get(c,t)) #if it is, replace _ necessary for config file with . which xml attributes use, assign the value in config
				else:
					conf[c][t]=config.get(c,t)
			except: #if no config tag exists, do nothing so we can move faster
				pass
		conf[c] = ut.dotdict(conf[c])
	conf['scriptRepo'] = scriptRepo
	conf['python'] = ut.pythonpath()
	conf = ut.dotdict(conf)			
	return conf

if __name__ == '__main__':
   unittest.main()	