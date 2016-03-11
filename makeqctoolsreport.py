# for pres
#mediainfo
#jhove
#framemd5
#send acc to R:\Visual\[0000]
import os
import subprocess
import sys

startObj = sys.argv[1]

#print ffprobe output to txt file, we'll grep it later to see if we need to transcode for j2k/mxf
ffdata = open(startObj + ".ffdata.txt","w")
subprocess.call(['ffprobe','-show_streams','-of','flat','-sexagesimal','-i',startObj], stdout=ffdata)
ffdata.close()

#transcode the j2k/mxf to rawvideo/.nut because qctools can't handle it natively (thanks DR)
subprocess.call(['ffmpeg','-vcodec','libopenjpeg','-vsync','0','-i',startObj,'-vcodec','rawvideo','-acodec','pcm_s24le','-vf','tinterlace=mode=merge,setfield=bff','-f','nut','-y',startObj + '.temp1.nut'])

#here's where we use ffprobe to make the qctools report in regular xml
tmpxml = open(startObj + '.qctools.xml','w')
subprocess.call(['ffprobe','-loglevel','error','-f','lavfi','movie=' + startObj + '.temp1.nut:s=v+a[in0][in1],[in0]signalstats=stat=tout+vrep+brng,cropdetect=reset=1,split[a][b];[a]field=top[a1];[b]field=bottom[b1],[a1][b1]psnr[out0];[in1]ebur128=metadata=1[out1]','-show_frames','-show_versions','-of','xml=x=1:q=1','-noprivate'], stdout=tmpxml)
tmpxml.close()

#gzip that tmpxml file then delete the regular xml file cause we dont need it anymore
subprocess.call(['C:/7-zip/7z.exe','a','-tgzip',startObj + '.qctools.xml.gzip',startObj + '.qctools.xml'])
tmps = [startObj + '.qctools.xml',startObj + '.ffdata.txt']
for f in tmps:
	os.remove(f)