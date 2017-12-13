'''
takes a picture with the 1st conencted camera
saves to desktop or to pre-defined path
'''

from __future__ import print_function

import logging
import os
import sys
import argparse
import re
import gphoto2 as gp
###UCSB modules###
import config as rawconfig
import util as ut
import logger as log

def main():
	'''
	do the thing
	'''
	conf = rawconfig.config()
	parser = argparse.ArgumentParser(description="captures image from first-connected camera")
	parser.add_argument('-nj', action='store_true', default=False, dest='nj', help='run with National Jukebox file destinations, on //svmwindows/special/78rpm')
	#parser.add_argument('-phi', action='store_true', default=False, dest="phi", help='run with PHI file destination, on ~/Desktop')
	args = parser.parse_args() #allows us to access arguments with args.argName
	logging.basicConfig(format='%(levelname)s: %(name)s: %(message)s', level=logging.WARNING)
	gp.check_result(gp.use_python_logging())
	context = gp.gp_context_new()
	camera = gp.check_result(gp.gp_camera_new())
	gp.check_result(gp.gp_camera_init(camera, context))
	print('Capturing image')
	file_path = gp.check_result(gp.gp_camera_capture(camera, gp.GP_CAPTURE_IMAGE, context))
	print('Camera file path: {0}/{1}'.format(file_path.folder, file_path.name))
	if args.nj:
		target = os.path.join(conf.NationalJukebox.VisualArchRawDir, file_path.name)
	#elif args.phi:
		#target = os.path.join(ut.desktop(), "phi_raw-image-captures", file_path.name)
	else:
		target = os.path.join(ut.desktop(), file_path.name)
	count = 0
	while os.path.exists(target):
		count = count + 1
		strcnt = str(count)
		while len(strcnt) < 4:
			strcnt = "0" + strcnt
		target = re.sub(r"capt\d*.cr2", "capt" + strcnt + ".cr2", target)
	print('Copying image to', target)
	camera_file = gp.check_result(gp.gp_camera_file_get(camera, file_path.folder, file_path.name, gp.GP_FILE_TYPE_NORMAL, context))
	gp.check_result(gp.gp_file_save(camera_file, target))
	#subprocess.call(['xdg-open', target])
	#gp.check_result(gp.gp_camera_exit(camera, context))

if __name__ == "__main__":
	sys.exit(main())
