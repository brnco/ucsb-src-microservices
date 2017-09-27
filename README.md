This document contains an overview of the various post-processing scripts we use here in the AVLab at UCSB's SRC.
Please see AVLab Utility Software List & Installation Instructions (on the wiki) for more info on the software used, dependencies, installation instructions, etc. The scripts described here build off of those software functionalities.

* [Intro](#intro)
* [makesomethings](#makesomethings)
   * [makebarcodes](#makebarcodes)
   * [makebroadcast](#makebroadcast)
   * [makedip](#makedip)
   * [makemp3](#makemp3)
   * [makeqctoolsreport](#makeqctoolsreport)
   * [makestartobject](#makestartobject)
   * [makereverse](#makereverse)
   * [makesip](#makesip)
   * [makevideoslices](#makevideoslices)
   * [makeyoutube](#makeyoutube)
* [library scripts](#library scripts)
   * [config](#config)
   * [ff](#ff)
   * [logger](#logger)
   * [mtd](#mtd)
   * [util](#util)
* [avlab](#avlab)
   * [avlab-audio](#avlab-audio)
   * [avlab-cylinders](#avlab-cylinders)
   * [avlab-discs](#avlab-discs)
   * [avlab-video](#avlab-video)
* [National Jukebox / PHI](#national-jukebox/PHI)
   * [nj_audio](#nj_audio)
   * [phi_discimg-capture-fm](#phi_discimg-capture-fm)
   * [phi_discimg-out](#phi_discimg-out)
* [Tips](#Tips)
* [hashmove](#hashmove)

# Intro
We use the microservices structure here, which breaks down complicated programs and processing steps into small, discreet, modular scripts, which can then be daisy-chained to fit particular applications.

To run these scripts, type python [path of python file] [arguments]

Every script can also be run with ypthon script.py -h for more info


# makesomething
the make-scripts are kind of the atomic units of our microservices. They work on single files and are very dumb but effective.

## makebarcodes
This script is used to generate barcode files that can be printed by our Zebra barcode printers. It makes a temporary file in your current directory. Then, for each side of a record, it asks for the title of the content, then the barcode: cusb_[label-abbrev]_[issue-number]_[copy(optional)]_[matrix-number]_[take-number]. Used for patron requests mostly. Once done, follow steps outlined in wiki doc Printing Barcodes

## makebroadcast
Takes an input file, generally an archival master or raw-broadcast capture, inserts 2s fades, drops bitrate to 44.1k/16bit, embeds ID3 metadata if source txt file is present.

Has flags for fades (-ff), national jukebox names (-nj), stereo (-s), normalize (-n)

## makedip
Takes an input string which is the canonical name for our digitized objects [a1234, cusb_col_a12_01_5678_00] and the transaction number from Aeon to which this DIP is linked. Transcodes from source objects if necessary, hashmoves them to DIP directory, zips DIP directory in anticipation of upload via FTP to Aeon server.

Has flags for startObject (-so), transactionNumber (-tn), mode (--tape for tapes, --disc coming soon), zip (-z) to make a .zip file
 
## makemp3
Takes an input file, generally a broadcast master, transcodes to 320kbps mp3. Embeds ID3 tags if present (either in source file or in sidecar txt file). Embeds png image of "Cover Art" if png or tif present in source directory.

## makeqctoolsreport
Takes an input video file, and outputs a compressed xml file that can be read by QCTools. It has to transcode it to a raw video format first so this script takes some time and processor space and is generally run Friday afternoon over a week of new captures, and runs into the weekend.

## makereverse
Takes an input file and stream-copies reversed slices of 600 seconds, then concatenates the slices back together. ffmpeg's areverse loads a whole file into memory, so for the large files we deal with we need this workaround.

## makesip
makesip takes an input folder path and uses our rules to create a SubmissionInformation Package (SIP)

## makestartobject
Takes a canonical name for an asset, e.g. a1234, cusb_col_a1234_01_5678_00, and returns a full path to an instance of that object. The instance is prioritized for transcoding in the following order: broadcast master, archival master, un-tagged archival master, access mp3.

## makevideoslices
Slices preservation and access transfers of videos with more than 1 asset on the tape (eg. vm1234 also contains vm5678 and vm9101). Takes no arguments but you have to edit the in and out points in a list in the script, as well as corresponding vNums. Needs to be better, OpenCube editing interface is crappy and Premiere doesn't accept our preservation masters so.....
 
## makeyoutube
Still in development, this script makes a youtube-ready video for a digitized 78rpm disc, based on metadata in DAHR

# library scripts

These scripts are basically collections of functions that are invoked by other scripts.

## config
config parses the microservices-config.ini file and returns a dictionary object that is accessible via dot notation, e.g. conf.cylinders.new_ingest rather than conf['cylinders']['new_ingest']. conf is declared globally in every script, this module is imported as rawconfig and conf = rawconfig.config() actually makes the conf dictionary.

## ff
ff does everything ffmpeg-related. principally, it uses the provided dictionary objects to construct strings that can be sent to ffmpeg. it also describes a framework ("ff.go") which runs the supplied ffmpeg string and returns true if successful, the error if unsuccessful

## logger
logger is the handler for all logging functions. Generally, it makes logs for each script's full execution, linking sub-scripts to their parents via PIDs. logs are named "user-pid-timestamp.log"

## mtd
mtd is short for "metadata" and it's the handler for all FileMaker and catalog access. It implements pyodbc an and SRU string to get metadata from external sources, or to insert metadata into FileMaker.

## util
util is the handler for all utility functions. Two noteworthy ones are: desktop() - which returns the current user's desktop folder; and dotdict(dict) - which takes a regular dictionary and makes it accessible via dot notation, e.g. conf.cylinders.new\_ingest rather than conf['cylinders']['new\_ingest']

# avlab
These processes deal with all of the audio objects created in the AVLab, not part of the Jukebox

## avlab-audio
Post-processing for magnetic-tape materials. Gets metadata from Audio Originals FileMaker db

Deletes sidecar files that Wavelab generates

makes a list of files to process based on FileMaker outputs (see staff wiki)

Deletes silences of longer than 30s

Embeds bext info, data chunk md5

hashmoves it to the repo directory, greps the output of hashmove and, if successful, deletes raw capture and assocaited txt files

## avlab-cylinders
Post-processing of cylinders and the creation of derivative files. Gets metadata from Cylinders FileMaker db.

## avlab-discs
Post-processing for discs that are not part of NJ process. Bundles makemp3 and makebroadcast with configurable filepaths. Used for post-processing of patron requests, mostly, saves files to a QC directory on R:/. Has dependencies for ffmpeg, ffprobe, bwfmetaedit

## avlab-video
post-processing for archival master video files. bundles makeqctoolsreport; makes a PBCore2.0 compliant xml file of technical metadata.

# National Jukebox / PHI
Here's the scripts we use to process materials for the National Jukebox/ PHI digitization project

## nj_audio
This script processes the archival and broadcast master files we make for the National Jukebox. For more info on how files are created, see Digitizing 78s for The National Jukebox on the wiki

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

## phi_discimg-capture
This script is used exclusively during disc label imaging and is called by FileMaker. It is run in conjunction with NJ Workflow DB's "discimg-in" script. For more info on the process of capturing disc label images, see Disc Imaging for National Jukebox

It takes arguments for a barcode / filename (which Filemaker provides)

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

## phi_discimg-out
This script is used to process an intermediate set of disc label digital images (created with Adobe DNG converter). For more info, see Disc Imaging for National Jukebox

It takes no arguments.

The processing steps are:

for each file in the intermediate directory

call GraphicsMagick to crop, rotate, adjust ppi, and save as tif in a new folder

here's what that command would look like if you typed it out for each file

gm convert [full path to input file] -crop 3648x3648+920 -density 300x300 -rotate 180 [full path to output .tif]

hashmove the raw-capture, dng intermediate, and broadcast tif to the qc directory/ purgatory

here's what that command would look like if you typed it out for each file

python hashmove.py [full path to input file] [full path to qc directory + /discname]



# Tips

### change your default cmd.exe directory to the repo directory

Start -> search "regedit" -> double-click "regedit.exe"

HKEY_CURRENT_USER -> Software -> Microsoft -> Command Processor

right click on the big empty space and select "new key"

type "Autorun" and hit enter

right-click "Autorun" in the regedit window and select "Edit"

type "cd/ d [path to repo directory]"

By doing this, you are set to open the cmd window in the directory with all the scripts so you don't have to type their full paths

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
