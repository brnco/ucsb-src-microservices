# for pres
#mediainfo
#jhove
#framemd5
#send acc to R:\Visual\[0000]
import os
import subprocess
import sys
import re

startObj = sys.argv[1]

#print ffprobe output to txt file, we'll grep it later to see if we need to transcode for j2k/mxf
ffdata = open(startObj + ".ffdata.txt","w")
subprocess.call(['ffprobe','-show_streams','-of','flat','-sexagesimal','-i',startObj], stdout=ffdata)
ffdata.close()

#find which stream is the video stream
ffdata = open(startObj + ".ffdata.txt","r")
for line in ffdata:
	#find the line for video stream
	if re.search('.codec_type=\"video\"', line):
		#separate that line by periods, the formatting provided by ffprobe
		foolist = re.split(r'\.', line)
		#3rd part of that list is the video stream
		whichStreamVid = foolist[2]
ffdata.close()

#based on the vid stream we found, find the codec
ffdata = open(startObj + ".ffdata.txt","r")
for line in ffdata:
	if re.search('streams.stream.' + whichStreamVid + '.codec_name=', line):
		#dunno why we gotta remove quotes twice but there ya go
		[f[1:-1] for f in re.findall('".+?"', line)]
		codecName = f[1:-1]
ffdata.close()
os.remove(startObj + ".ffdata.txt") #only takes a string so cant send ffdata var idk

#set some special strings to handle j2k/mxf files
if codecName == 'jpeg2000':
	inputCodec = ' -vcodec libopenjpeg '
	filterstring = ' -vf tinterlace=mode=merge,setfield=bff '
else:
	inputCodec = ' '
	filterstring = ' '

#transcode to .nut	
ffmpegstring = 'ffmpeg' + inputCodec + '-vsync 0 -i ' + startObj + ' -vcodec rawvideo -acodec pcm_s24le' + filterstring + '-f nut -y ' + startObj + '.temp1.nut'
subprocess.call(ffmpegstring)

#here's where we use ffprobe to make the qctools report in regular xml
print "writing ffprobe output to xml"
tmpxml = open(startObj + '.qctools.xml','w')
subprocess.call(['ffprobe','-loglevel','error','-f','lavfi','movie=' + startObj + '.temp1.nut:s=v+a[in0][in1],[in0]signalstats=stat=tout+vrep+brng,cropdetect=reset=1,split[a][b];[a]field=top[a1];[b]field=bottom[b1],[a1][b1]psnr[out0];[in1]ebur128=metadata=1[out1]','-show_frames','-show_versions','-of','xml=x=1:q=1','-noprivate'], stdout=tmpxml)
tmpxml.close()

#gzip that tmpxml file then delete the regular xml file cause we dont need it anymore
print "gzip-ing ffprobe xml output"
subprocess.call(['C:/7-zip/7z.exe','a','-tgzip',startObj + '.qctools.xml.gz',startObj + '.qctools.xml'])
os.remove(startObj + '.qctools.xml')
os.remove(startObj + '.temp1.nut')