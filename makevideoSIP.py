#makevideoSIP
#takes argument for video package (folder) and optional arg for -lto, which writes package to lto5
#verifies all contents of SIP exist: -pres.mxf and -acc.mp4 files, -pres.mxf.PBCore2.0.xml metadata, -pres.mxf.framemd5 hash, -pres.qctools.xml.gz report, -pres.mxf.md5 and -acc.mp4.md5 hashes
#copies -acc.mp4 and ancillary data to vNumber folder on R:/
#gzips video package folder package
#logs manifest of all files present in SIP, hash of gzip, and assigns packageID
#-lto writes this data to our lto drive, logs the barcode of the lto tape

def main():
	#parser
	#get names
	#verify()
	#copy()
	#gzip()
	#writelog()
	#subprocess.call('python','writelto.py')
	return
