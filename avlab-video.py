# for pres
#mediainfo
#jhove
#framemd5
#send acc to R:\Visual\[0000]
import os
import subprocess
import sys

startObj = sys.argv[1]
ffdata = open(startObj + ".ffdata.txt","w")
subprocess.call(['ffprobe','-show_streams','-of','flat','-sexagesimal','-i',startObj], stdout=ffdata)
ffdata.close()
subprocess.call(['ffmpeg','-vcodec','libopenjpeg','-vsync','0','-i',startObj,'-vcodec','rawvideo','-acodec','pcm_s24le','-vf','tinterlace=mode=merge,setfield=bff','-f','nut','-y',startObj + '.temp1.nut'])
tmpxml = open(startObj + '.qctools.xml','w')
subprocess.call(['ffprobe','-loglevel','error','-f','lavfi','movie=' + startObj + '.temp1.nut:s=v+a[in0][in1],[in0]signalstats=stat=tout+vrep+brng,cropdetect=reset=1,split[a][b];[a]field=top[a1];[b]field=bottom[b1],[a1][b1]psnr[out0];[in1]ebur128=metadata=1[out1]','-show_frames','-show_versions','-of','xml=x=1:q=1','-noprivate'], stdout=tmpxml)
tmpxml.close()
subprocess.call(['C:/7-zip/7z.exe','a','-tgzip',startObj + '.qctools.xml.gzip',startObj + '.qctools.xml'])
os.remove(tmpxml)