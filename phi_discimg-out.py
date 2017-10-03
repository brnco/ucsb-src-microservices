'''
#phi_discimg-out
#processes intermediate dng files to tiff
#moves all image files to qcDir
'''
import ConfigParser
import argparse
import subprocess
import os
import sys
import time
import getpass
import re
import rawpy
import imageio
from PIL import Image
from distutils import spawn
###UCSB modules###
import config as rawconfig
import util as ut
import logger as log
import mtd
import makestartobject as makeso
	
def idSize(fname,endDir):
	'''
	images come in off the camera in the wrong orientation
	this returns the correct orientation, given that the image should be landscape
	and image is never at correct orientation as it comes off camera
	'''
	img = Image.open(os.path.join(endDir,fname + ".tif"))
	if img.width > img.height:
		rotation = 180
	else:
		rotation = 90			
	if rotation:
		return rotation
	else:
		print "buddy, something's up"
		log.log({"message":"something is wrong with the rotation calculation","level":"error"})
		sys.exit()
	
def rawpyToTif(startObjFP,fname,endDir):
	'''
	converts the raw cr2 file to tiff
	'''
	#output = subprocess.check_output(['gm','convert',startObjFP,'-rotate',rotation,'-crop','3648x3648+920','-density','300x300',os.path.join(endDir,fname + ".tif")])
	with rawpy.imread(startObjFP) as raw:
		rgb = raw.postprocess(use_camera_wb=True)
	imageio.imsave(os.path.join(endDir,fname + ".tif"),rgb)	
	

def rotateTif(startObjFP,fname,rotation,endDir):	
	'''
	rotates the tiff
	'''
	img = Image.open(os.path.join(endDir,fname + ".tif"))
	img2 = img.rotate(rotation,expand=True)
	img2.save(os.path.join(endDir,fname + "-rotated.tif"))
	time.sleep(2)
	os.remove(os.path.join(endDir,fname + ".tif"))
	os.rename(os.path.join(endDir,fname + "-rotated.tif"),os.path.join(endDir,fname + ".tif"))

def cropTif(startObjFP,fname,endDir):
	'''
	crops the tif to largest possible square
	'''
	img = Image.open(os.path.join(endDir,fname + ".tif"))
	img2 = img.crop((920,0,img.width-920,3656))
	img2.save(os.path.join(endDir,fname + "-cropped.tif"))
	time.sleep(2)
	os.remove(os.path.join(endDir,fname + ".tif"))
	os.rename(os.path.join(endDir,fname + "-cropped.tif"),os.path.join(endDir,fname + ".tif"))
	output = subprocess.check_output([conf.python,os.path.join(conf.scriptRepo,'hashmove.py'),'-nm',os.path.join(endDir,fname + ".tif")])
	log.log(output)

	
def tifToJpg(startObjFP,fname,endDir):
	'''
	converts the tiff to jpeg
	'''
	img = Image.open(os.path.join(endDir,fname + ".tif"))
	img.save(os.path.join(endDir,fname + ".jpg"),"JPEG",quality=100)
	#output = subprocess.check_output(['gm','convert',os.path.join(endDir,fname + ".tif"),'-resize','800x800',os.path.join(endDir,fname + ".jpg")])
	#with rawpy.imread(startObjFP) as raw:
		#rgb = raw.postprocess(use_camera_wb=True)
	#imageio.imsave(os.path.join(endDir,fname + ".jpg"),rgb)
	output = subprocess.check_output([conf.python,os.path.join(conf.scriptRepo,'hashmove.py'),'-nm',os.path.join(endDir,fname + ".jpg")])
	log.log(output)

def moveSO(startObjFP,endDir):
	'''
	hashmoves the original cr2 to pre-ingest-qc
	'''
	output = subprocess.check_output([conf.python,os.path.join(conf.scriptRepo,'hashmove.py'),startObjFP,endDir])
	log.log(output)
	
def main():
	'''
	do the thing
	'''
	global conf
	conf = rawconfig.config()
	parser = argparse.ArgumentParser(description="processes image files for disc labels")
	parser.add_argument('-i','--input',dest='i',help="the rawcapture file.cr2 to process, not full path")
	parser.add_argument('-m','--mode',dest='m',choices=["single","batch"],help='mode, process a single file or every file in capture directory')
	args = parser.parse_args()
	imgCaptureDir = conf.NationalJukebox.VisualArchRawDir
	print conf.NationalJukebox.VisualArchRawDir
	log.log("started")
	if args.m == "single":
		startObj = startObjFP = args.i.replace("\\","/")
		if not startObj.startswith(imgCaptureDir):
			for dirs,subdirs,files in os.walk(imgCaptureDir):
				for f in files:
					if f == startObj:
						startObjFP = os.path.join(dirs,startObj)
						break
			if not os.path.exists(startObjFP):
				print("Object " + startObj + " does not exist in " + imgCaptureDir)
				foo = raw_input("You should check on that or try a different filename")
				sys.exit()
		else:
			startObjFP = startObj
		fname,ext = os.path.splitext(startObj)
		endDir = os.path.join(conf.NationalJukebox.PreIngestQCDir,fname)
		if not os.path.exists(endDir):
			os.makedirs(endDir)
		
		
		#convert to tif
		rawpyToTif(startObjFP,fname,endDir)
		
		#get the orientation of the image and set output rotation accordingly
		rotation = idSize(fname,endDir)

		#rotate the tif
		rotateTif(startObjFP,fname,rotation,endDir)
		
		#crop the tif
		cropTif(startObjFP,fname,endDir)
		
		#convert to jpg
		#should make jpeg from tiff moving forward
		tifToJpg(startObjFP,fname,endDir)
		
		#move startObj
		moveSO(startObjFP,endDir)

	elif args.m == "batch":
		for dirs,subdirs,files in os.walk(imgCaptureDir):
			for f in files:
				if not f.endswith(".DS_Store"):
					startObj = f
					startObjFP = os.path.join(dirs,f)
					fname,ext = os.path.splitext(f)
					endDir = os.path.join(conf.NationalJukebox.PreIngestQCDir,fname)
					if not os.path.exists(endDir):
						os.makedirs(endDir)
					print f
					#convert to tif
					rawpyToTif(startObjFP,fname,endDir)

					#get the orientation of the image and set output rotation accordingly
					rotation = idSize(fname,endDir)
					
					#rotate the tif
					rotateTif(startObjFP,fname,rotation,endDir)
					
					#crop the tif
					cropTif(startObjFP,fname,endDir)
					
					#convert to jpg
					#should make jpeg from tiff moving forward
					tifToJpg(startObjFP,fname,endDir)
					
					#move startObj
					moveSO(startObjFP,endDir)

if __name__ == '__main__':					
	main()
	log.log("complete")