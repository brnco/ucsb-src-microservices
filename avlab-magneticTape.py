#avlab-magneticTape


#takes files rooted at capture dir
#renames based on FM output
#changeschannels based on FM output
#silenceremove
#ffmpeg -i [input] -af silenceremove=0:0:-50dB:-10:1:-50dB -acodec pcm_s24le [output]
#split files larger than 2GB
#embed checksums
#embed bext metadata based on FM output
#hashmove to repo folder