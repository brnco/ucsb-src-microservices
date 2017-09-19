import os
import imp
import re
import pyodbc
import subprocess
import string
import shutil

def get_existing_md5(md5str):
	match = ''
	match = re.search('\w{32}',md5str)
	if match:
		md5 = match.group()
		return md5
	else:
		return None

def get_existing_fileinstance(md5str):	
	match = ''
	match = re.search('cusb.*',md5str)
	if match:
		fileinstance = match.group()
		return fileinstance
	else:
		return None

def nth_parent(path, n): return path if n <= 0 else os.path.dirname(nth_parent(path, n-1))

def get_accession_md5_fileinstance(dirs, f):
	afh = {}
	md5filepath = os.path.join(dirs,f + ".md5")
	afh["id"] = nth_parent(md5filepath,2).replace("I:/","")
	if not afh["id"]:
		afh["id"] = nth_parent(md5filepath,1).replace("I:/","")
	if os.path.exists(md5filepath):
		md5fileobj = open(md5filepath,"r")
		md5str = md5fileobj.read()
		afh["hash"] = get_existing_md5(md5str)
		afh["filename"] = get_existing_fileinstance(md5str)
		return afh
	else:
		print "buddy, you gotta make a hash for "
		print f
		return None

def separateLTOpacket(s):
	print s
	sfull = "I:/" + s
	endDirThousand = s.replace("v","")[:1]
	endDirThousand = endDirThousand + "000"
	dest = os.path.join(conf.video.repo,endDirThousand,s)
	print dest
	if not s.startswith("F") and not os.path.exists(dest):
		print "copying " + s
		shutil.copytree(sfull,dest,ignore=shutil.ignore_patterns("*.mxf","*.mxf.md5"))
	print "bagging " + s
	#subprocess.call([conf.python,"S:/avlab/bagit-python/bagit.py"),'--md5',sfull])
	md5 = "md5"
	bagit.make_bag(sfull, checksums=[md5])
	if not os.path.exists(os.path.join(dest,"baginfo")):
		os.makedirs(os.path.join(dest,"baginfo"))
	print "copying baginfo"
	for f in os.listdir(sfull):
		if f.endswith(".txt"):
			shutil.copy2(os.path.join(sfull,f),os.path.join(dest,"baginfo"))		

def frameRate_Original_bug_check(s1,fullpath):
	fro_bug_str = 'fail! ' + fullpath + '''
   --  [fail:master_format_policy.mxf]
   --   [fail:Video/FrameRate_Original is 59.940]'''
	remove = string.punctuation + string.whitespace
	return s1.translate(None, remove) == fro_bug_str.translate(None, remove)

def check_format_policy(fullpath):
	if "mxf" in fullpath:
		policy = conf.video.master_format_policy
	elif "mp4" in fullpath:
		policy = conf.video.access_format_policy
	output = subprocess.check_output(["mediaconch","-p",policy,fullpath])
	if output.startswith("fail"):
		fro_bug = frameRate_Original_bug_check(output,fullpath)
		if fro_bug is True:
			return True
		else:
			print "failed master"
			print output
			policy = conf.video.ff_master_format_policy
			output = subprocess.check_output(["mediaconch","-p",policy,fullpath])
			if output.startswith("fail"):
				print "failed ff_master"
				#print output
				if "AudioCount" in output:
					print "needs new audio"
					return False
			else:
				return True
	else:
		return True
			
def get_hash_fromFM(fname):
	sqlstr = """select
				hash from file_instance
				where filename = '""" + fname + "'"
	hash = makemtd.queryFM_single(sqlstr,pyodbc.connect(conf.video.cnxn))
	if hash:
		hash = hash[0]
	else:
		hash = None
	return hash

def get_hash_on_disk(fullpath):
	try:
		hashondisk = subprocess.check_output(['python','S:/avlab/microservices/hashmove.py','-nm','-np',fullpath])
		print hashondisk
		rtncode = 0
	except subprocess.CalledPRocessError,e:
		rtncode = e
	if rtncode:
		print "bud there was a problem with " + fullpath
	else:
		match = ''
		match = re.search(r'\w{32}',hashondisk)
		if match:
			return match.group()
		else:
			return False
		
def main():
	global ut
	ut = imp.load_source("ut","S:/avlab/microservices/util.py")
	global conf
	rawconfig = imp.load_source('config',"S:/avlab/microservices/config.py")
	conf = rawconfig.config()
	global makemtd
	makemtd = imp.load_source('makemtd',"S:/avlab/microservices/makemetadata.py")
	global bagit
	bagit = imp.load_source("bagit","S:/avlab/bagit-python/bagit.py")
	for dirs,subdirs,files in os.walk("I:/"):	
		for f in files:
			if f.endswith(".mxf"):
				print ""
				print f
				fullpath = os.path.join(dirs,f)
				fmhash = get_hash_fromFM(f)
				hashondisk = get_hash_on_disk(fullpath)
				if hashondisk:
					print hashondisk
					print fmhash
					if not hashondisk == fmhash.lower():
						print "buddy, check on " + f
						print "becase the hashes don't match"
						foo = raw_input("eh")
					else:
						continue
				'''meets_policy = check_format_policy(fullpath)
				if meets_policy is True:
					print "pass!"
				#if not os.path.exists(os.path.join(dirs,f + ".qctools.xml.gz")):
					#subprocess.call(['python','S:/avlab/microservices/makeqctoolsreport.py','-so',os.path.join(dirs,f)])
				#if not os.path.exists(os.path.join(dirs,f + ".PBCore2.xml")):
					#subprocess.call(['mediainfo','--Output=PBCore2','--LogFile=' + os.path.join(dirs,f + ".PBCore2.xml"),os.path.join(dirs,f)])
				#os.remove(os.path.join(dirs,f))
				afh = get_accession_md5_fileinstance(dirs,f)
				print afh
				cnxn = pyodbc.connect(conf.video.cnxn)
				afh['materialType'] = 'video'
				makemtd.insertHash(cnxn,**afh)'''
main()