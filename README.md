This document contains an overview of the various post-processing scripts we use here in the AVLab at UCSB's SRC.
Please see AVLab Utility Software List & Installation Instructions (on the wiki) for more info on the software used, dependencies, installation instructions, etc. The scripts described here build off of those software functionalities.
 
# Intro
We use the microservices structure here, which breaks down complicated programs and processing steps into small, discreet, modular scripts, which can then be daisy-chained to fit particular applications.

To run these scripts, type python [path of python file] [arguments]
 
# Configuration
After cloning from the github repo, there are a couple of steps necessary to make these scripts go, on Windows. 

### The first step is:
set up a config file using the microservices-config-template.txt file found in the repo

Save it in the same dir as this repo

rename it to microservices-config.ini

open this file in a text editor and fill out the fields

example, under global -> scriptRepo:

put the full path to the directory in which you cloned the github repo

this way python knows where to draw sub-scripts from

Do the same for the paths of other workflow stages

### The second step (and this isn't strictly necessary) is to:

change your default cmd.exe directory to the repo directory

Start -> search "regedit" -> double-click "regedit.exe"

HKEY_CURRENT_USER -> Software -> Microsoft -> Command Processor

right click on the big empty space and select "new key"

type "Autorun" and hit enter

right-click "Autorun" in the regedit window and select "Edit"

type "cd/ d [path to repo directory]"

By doing this, you are set to open the cmd window in the directory with all the scripts so you don't have to type their full paths

# makesomethings
the make-scripts are kind of the atomic units of our microservices. They work on single files and are very dumb but effective.

## makebroadcast
Takes an input file, generally an archival master or raw-broadcast capture, inserts 2s fades, drops bitrate to 44.1k/16bit, embeds ID3 metadata if source txt file is present.

Has dependencies for ffmpeg, ffprobe. Takes 1 argument for file to process. Has flags for fades (-ff), national jukebox names (-nj), stereo (-s).

"python makebroadcast.py -h" for more info
 
## makemp3
Takes an input file, generally a broadcast master, transcodes to 320kbps mp3. Embeds ID3 tags if present (either in source file or in sidecar txt file). Embeds png image of "Cover Art" if png or tif present in source directory.

Has dependencies for ffmpeg, ffprobe, graphicsmagick. Takes 1 argument for full path of file to process.

"python makemp3.py -h" for more info

## makereverse
Takes an input file and stream-copies reversed slices of 600 seconds, then concatenates the slices back together. ffmpeg's areverse loads a whole ifle into memory, so for the large files we deal with we need this workaround.

Has dependencies for ffmpeg. Takes 1 arg of the path to the file to process

"python makereverse.py -h" for more info

## makeffmetadata
Takes input for canonical asset name [a1234, cusb_col_a12_01_5678_00] and title, performer, album, and date, and makes an ;FFMETADATA text file suitable for ffmpeg to embed in a broadcast master or mp3 as ID3 tags. Is most often called by FileMaker, particularly for cylinders, or by makebroadcast

Has dependencies for ffmpeg, ffprobe

Has flags for cylinder (-cyl), disc (-disc), tape (-tape), that correspond to different ID3 templates. also has flags for title (-t), album (-a), performer (-p), copyright (-r), and date (-d)

"python makeffmetadata.py -h" for more info
 
For info on making ID3 source files see: http://jonhall.info/how_to/create_id3_tags_using_ffmpeg

## makebext
Takes an input for canonical asset name [a1234, cusb_col_a12_01_5678_00] and a set of strings to be concatenated into a call to bwfmetaedit, prints a text file to given directory for asset type (tape, disc, etc). Used almost exclusively to format FileMaker outputs.

Has 0 dependencies

Has flags for start object (-so), tape (-tape, disc and cylinder coming soon), date (-d), master key (-mk), title (-t), manuscript number (-mss), collection name (-c).
 
## makeqctoolsreport
Takes an input video file, and outputs a compressed xml file that can be read by QCTools. It has to transcode it to a raw video format first so this script takes some time and processor space and is generally run Friday afternoon over a week of new captures, and runs into the weekend.

Has dependencies for ffmpeg, ffprobe. Takes argument for full path of file to be processed.

"python makeqctoolsreport.py -h" for more info.

## makebarcodes
This script is used to generate barcode files that can be printed by our Zebra barcode printers. It makes a temporary file in your current directory. Then, for each side of a record, it asks for the title of the content, then the barcode: cusb_[label-abbrev]_[issue-number]_[copy(optional)]_[matrix-number]_[take-number]. Used for patron requests mostly. Once done, follow steps outlined in Printing Barcodes

Has 0 dependencies. Takes no arguments.

## makevideoslices
Slices preservation and access transfers of videos with more than 1 asset on the tape (eg. vm1234 also contains vm5678 and vm9101). Takes no arguments but you have to edit the in and out points in a list in the script, as well as corresponding vNums. Needs to be better, OpenCube editing interface is crappy and Premiere doesn't accept our preservation masters so.....

Has dependencies for ffmpeg, ffprobe

## makedip
Takes n input strings that are the canonical names for our digitized objects [a1234, cusb_col_a12_01_5678_00] and the transaction number from Aeon to which this DIP is linked. Transcodes from source objects if necessary, hashmoves them to DIP directory, zips DIP directory in anticipation of upload via FTP to Aeon server. Flags for "high quality" and "archival" not yet working (patrons sometimes request these).

Has dependencies for ffmpeg, ffprobe

Has flags for startObject (-so), transactionNumber (-tn), mode (-tape for tapes, -disc coming soon)

python makedip.py -h for more info
 
## makevideoSIP (DEPRECATED)
Take an argument of the vNumber (accession number for video) and outputs .tar.gz file for storage on LTO.

Has dependencies for ffmpeg, ffprobe



# avlab
These processes deal with all of the audio objects created in the AVLab, not part of the Jukebox

## avlab-audio
Post-processing for magnetic-tape materials. Takes no arguments, has dependencies for ffmpeg, ffprobe, bwfmetaedit
Deletes sidecar files that Wavelab generates

makes a lsit of files to process based on FileMaker outputs (see staff wiki)

Deletes silences of longer than 10s, calls changechannels to correct any channel configuration mismatches

Embeds bext info, data chunk md5

hashmoves it to the repo directory, greps the output of hashmove and, if successful, deletes raw capture and assocaited txt files

## avlab-cylinders
Post-processing of cylinders and the creation of derivative files for ingest to the R:/ drive/ site.
The key here is that you have to export the metadata from fm via makeffmetadata and it embeds in our broadcast masters and everything else downstream.

## avlab-discs
Post-processing for discs that are not part of NJ process. Bundles makemp3 and makebroadcast with configurable filepaths. Used for post-processing of patron requests, mostly, saves files to a QC directory on R:/. Has dependencies for ffmpeg, ffprobe, bwfmetaedit

## avlab-discimg-out
This script uses GraphicsMagick to transcode from .dng to .tif, cropping, rotating, and changing the dpi of the files in the process, according to LC's specs. It then hashmoves them to the avlab/new_ingest/pre-ingest-qc folder. For more info, see Imaging Disc Labels on the staff wiki

## avlab-video
post-processing for archival master video files. bundles makeqctoolsreport; generates frame level checksums with framemd5; makes a PBCore2.0 compliant xml file of technical metadata.

## changechannels
This script is used to edit the channel configuration of raw audio captures.

Has 1 dependency for ffmpeg. Takes arguments for file(s) to be processed.

## listen2transfers-qc.py
This script automatically walks you through the last n days of audio transfers, listening starting at the 1min mark. You listen to 1/3 of the total transfers with this.

Has dependencies for ffplay.

Has arguments: -t to listen to magnetic tape transfers; -c to lsiten to cylinder transfers; -nj to listen to National Jukebox transfers; -d followed by a number for the number of days back to look, default 7.

# National Jukebox
Here's the scripts we use to process materials for the National Jukebox

## nj_audio
This script processes the archival and broadcast master files we make for the National Jukebox. For more info on how files are created, see Digitizing 78s for The National Jukebox on the wiki

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

## nj_discimg-capture-fm
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

## nj_discimg-out
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

## nj_pre-SIP
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

# hashmove

file movement for people wihtout rsync

**General Usage**

python hashmove.py [source file or directory full path] [destination parent directory full path] [flags]

**to move a file**

python hashmove.py C:/path/to/file.ext C:/path/to/parent/dir

**to move a directory**

python hashmove.py /home/path/to/dir/a /home/path/to/dir/b

**to copy a file**

python hashmove.py C:/path/to/file.ext C:/path/to/parent/dir -c

**log the transfer**

python hashmove.py /home/path/to/dir/a /home/path/to/dir/b -l

**verify against another hash or set of hashes**

python hashmove.py "/home/path to/dir/you question" /home/path/to/dir/with/hashes -v
