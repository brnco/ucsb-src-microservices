This document contains an overview of the various post-processing scripts we use here in the AVLab at UCSB.
Please see AVLab Utility Software List & Installation Instructions for more info on the software used, dependencies, installation instructions, etc. The scripts described here build off of these software functionalities.
 
#Intro
We use the microservices structure here, which breaks down complicated programs and processing steps into small, discreet, modular scripts, which can then be daisy-chained to fit particular applications.

for programs with .exe extensions you can simply type their full path into the cmd.exe window and they'll go
for .py extensions, you need to have python installed, and you type python [path of python file] [arguments]
 
#Configuration
After cloning from the github repo, there are a couple of steps necessary to make these scripts go, on Windows. 

###The first is:
set up a config file using the microservices-config-template.ini file found in the repo

Move this file to C:/Users/[username]/

rename it to microservices-config.ini

open this file in a text editor and fill out the fields

example, under global -> scriptRepo:

put the full path to the directory in which you cloned the github repo

this way python knows where to draw sub-scripts from

Do the same for the paths of other workflow stages

###The second step (and this isn't strictly necessary) is to:

change your default cmd.exe directory to the repo directory

Start -> search "regedit" -> double-click "regedit.exe"

HKEY_CURRENT_USER -> Software -> Microsoft -> Command Processor

right click on the big empty space and select "new key"

type "Autorun" and hit enter

right-click "Autorun" in the regedit window and select "Edit"

type "cd/ d [path to repo directory]"

By doing this, you are set to open the cmd window in the directory with all the scripts so you don't have to type their full paths
 
 
 

#hashmove
hashmove takes two arguments: 1) the source file or directory and 2) the destination directory. For files, hashmove just copies from source to destination, writes md5 hashes of both source and destination files, compares the hashes, and if they're the same it deletes the source file and source file hash. If different it throws out a warning and does not delete. For directories, it does the same thing after making a list of every file in the source directory. If initial .md5 files are present in source, they are not overwritten (and are assumed to be correct and up-to-date). You can give it Windows or POSIX paths and it'll work (needs testing) and it can only handle 1 layer of subdirectories.

hashmove forms the basis of all asset-file-moving operations in these scripts. By doing this complicated routine, we can actually verify that the files we have are the ones we think they are. This is important for things like video, where, over the course of a 40GB transfer, the opportunities for things to get lost, and the costs of re-transfer, are high. There are utilities such as rsync, bbcp, and BagIt that do this kind of thing, but these were deemed too complicated to implement/ too blackbox-esque/ or were unavailable on Windows.

Has 0 dependencies. Takes 2 arguments for source and destination. Has flag for copy instead of move (-c).

"python hashmove.py -h" for more info




#makesomethings
the make-scripts are kind of the atomic units of our microservices. They work on single files and are very dumb but effective.

##makedip
always makes me think of hummus

Takes n input strings that are the canonical names for our digitized objects [a1234, cusb_col_a12_01_5678_00] and the transaction number from Aeon to which this DIP is linked. Transcodes from source objects if necessary, hashmoves them to DIP directory, zips DIP directory in anticipation of upload via FTP to Aeon server. Flags for "high quality" and "archival" not yet working (patrons sometimes request these).

Has dependencies for ffmpeg, ffprobe

Has flags for startObject (-so), transactionNumber (-tn)

python makedip.py -h for more info

##makebroadcast
Takes an input file, generally an archival master or raw-broadcast capture, inserts 2s fades, drops bitrate to 44.1k/16bit, embeds ID3 metadata, if source txt file is present.

Has dependencies for ffmpeg, ffprobe. Takes 1 argument for file to process. Has flags for fades (-ff), national jukebox names (-nj), stereo (-s).

"python makebroadcast.py -h" for more info

For info on making ID3 source files see: http://jonhall.info/how_to/create_id3_tags_using_ffmpeg
 
##makemp3
Takes an input file, generally a broadcast master, transcodes to 320kbps mp3. Embeds ID3 tags if present (either in source file or in sidecar txt file). Embeds png image of "Cover Art" if png or tif present in source directory.

Has dependencies for ffmpeg, ffprobe, graphicsmagick. Takes 1 argument for full path of file to process.

"python makemp3.py -h" for more info
 
##makeqctoolsreport.py
Takes an input video file, and outputs a compressed xml file that can be read by QCTools. It has to transcode it to a raw video format first so this script takes some time and processor space and is generally run Friday afternoon over a week of new captures, and runs into the weekend.

Has dependencies for ffmpeg, ffprobe. Takes argument for full path of file to be processed.

"python makeqctoolsreport.py -h" for more info.

##makebarcodes.py
This script is used to generate barcode files that can be printed by our Zebra barcode printers. It makes a temporary file in your current directory. Then, for each side of a record, it asks for the title of the content, then the barcode: cusb_[label-abbrev]_[issue-number]_[copy(optional)]_[matrix-number]_[take-number]. Used for patron requests mostly. Once done, follow steps outlined in Printing Barcodes

Has 0 dependencies. Takes no arguments.
 


#avlab
These processes deal with all of the audio objects created in the AVLab, not part of the Jukebox

##avlab-magneticTape
This was the hardest one to write because there's so many moving parts.
It consists of a FOR loop that: goes through our default directory, file by file;
asks if a file is mono or stereo;
if mono, asks if it's longer than 2hrs and breaks it into 2hr chunks if it is; 
if stereo, asks if a file is longer than 1hr, breaks it into 1hr long chunks if it is; 
if it has been sliced in this way it also deletes the raw transfer; leaves the file alone if it doesn't meet those conditions; 
embeds bwf data where it exists; 
embeds a checksum for audio data; 
copies the file to the appropriate directory on the R:\ drive; 
writes whole-file checksums of both the local and repository copies of the files; 
compares the whole-file checksums, and if they match, deletes the local copy; 
and on exit it deletes the empty directories left behind by that other deletion process.
I should really make a video tutorial for this.


##avlab-cylinders
This script automates the post-processing of cylinders and the creation of derivative files for ingest to the R:\ drive/ site.
The key here is that you have input some metadata by hand so that it embeds nicely in our downloadable mp3 files.
Also, for batches of cylinders, you're gonna want to NOT use this and write a custom script.

##avlab-discs
Post-processing for discs that are not part of NJ process. Bundles makemp3 and makebroadcast with some hard-coded filepaths. Used for post-processing of patron requests, mostly, saves files to a QC directory on R:/

##avlab-discimg-out
This script uses GraphicsMagick to transcode from .dng to .tif, cropping, rotating, and changing the dpi of the files in the process, according to LC's specs. It then hashmoves them to the avlab/new_ingest/pre-ingest-qc folder.

##avlab-video.py
post-processing for archival master video files. bundles makeqctoolsreport; generates frame level checksums with framemd5; makes a PBCore2.0 compliant xml file of technical metadata.

##changechannels.py
This script is used to edit the channel configuration of raw audio captures.
Has 1 dependency for ffmpeg. Takes arguments for file(s) to be processed.


#National Jukebox
Here's the scripts we use to process materials for the National Jukebox

##nj_audio
This script processes the archival and broadcast master files we make for the National Jukebox. For more info on how files are created, see Digitizing 78s for The National Jukebox
It has dependencies for ffmpeg and ffprobe. It takes no arguments
The processing steps are:
delete the bs sidecar files that Wavelab creates
ending in .bak .gpk .mrk
makebroadcast on the raw-broadcast-master files, inserting fades and renaming for nj
here's what that command would look like if you typed it out for each file
python makebroadcast.py [full path to input file] -ff -nj
hashmove the now-processed broadcast masters to the qc directroy/ purgatory
here's what that command would look like if you typed it out for each file
python hashmove.py [full path to input file] [full path to qc directory + /discname]
use bwf metaedit to embed MD5 hashes into the MD5 chunk
here's what that command would look like if you typed it out for each file
bwfmetaedit --MD5-Embed [full path to input file]
hashmove the now-processed archival masters to the qc directory/ purgatory
here's what that command would look like if you typed it out for each file
python hashmove.py [full path to input file] [full path to qc directory + /discname]

##nj_discimg-capture-fm
This script is used exclusively during disc label imaging and is called by FileMaker. It is run in conjunction with NJ Workflow DB's "discimg-in" script. For more info on the process of capturing disc label images, see Disc Imaging for National Jukebox
It has 0 dependencies. It takes arguments for a barcode / filename (which Filemaker provides)
The processing steps are:
do a string substitution for "ucsb" to "cusb
corrects a long-standing programming error in FM
using the filename provided, check that it doesn't already exist in the capture directory
return an error if it does
sort the capture dir by file creation date
rename the most recently created file to the barcode/filename provided
walk through the capture directory and check to see that no files exist with their raw-capture names
this indicates that we missed scanning a barcode
return an error if true

##nj_discimg-out
This script is used to process an intermediate set of disc label digital images (created with Adobe DNG converter). For more info, see Disc Imaging for National Jukebox
It has 1 dependency for GraphicsMagick. It takes no arguments.
The processing steps are:
for each file in the intermediate directory
call GraphicsMagick to crop, rotate, adjust ppi, and save as tif in a new folder
here's what that command would look like if you typed it out for each file
gm convert [full path to input file] -crop 3648x3648+920 -density 300x300 -rotate 180 [full path to output .tif]
hashmove the raw-capture, dng intermediate, and broadcast tif to the qc directory/ purgatory
here's what that command would look like if you typed it out for each file
python hashmove.py [full path to input file] [full path to qc directory + /discname]

##nj_qc
This script is used to verify the contents of a directory in our qc holding pen. If it meets the requirements for filetypes necessary for SIPping to LC, move it to our batch folder.
It has 0 dependencies. It takes no arguments.
The processing steps are:
make sure that everything has been renames from "ucsb" to "cusb"
I can't stress enough what a bother this is
walk through the subdirectories of the qc directory, which are named with the disc filenames
verify that:
an archival master exists (m.wav)
a broadcast master exists (.wav)
a broadcast image exists (.tif)
If true, hashmove that directory to our batch folder (containing 1000 SIPs)
here's what that command would look like if you typed it out for each file
python hashmove.py [full path to input directory] [full path to batch directory]
