::makemp3 takes an argument for filename
::if images, metadata exist they'll be embedded
::gotta cd into the dir where the file is
::see url for more info http://jonhall.info/how_to/create_id3_tags_using_ffmpeg

@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

set startObj=%1

::grab filename and initialize a bunch of crap
set filename=!startObj:~0,-5!
set mtdObj=!filename!.txt
set intermediateObj=!filename!e.mp3
set endObj=!filename!d.mp3
set startimageObj=!filename!.tif
set endimageObj=!filename!.png

::actually make the thing part 1
ffmpeg -i !startObj! -ar 44100 -ab 320k -f mp3 -id3v2_version 3 -write_id3v1 1 !intermediateObj!

::actually make the thing part 2
::make a plain mp3 if theres no image object
if not exist !startimageObj! (
	ren !intermediateObj! !endObj!
)
::if there is an image object make a nice mp3
if exist !startimageObj! (
	if not exist !endimageObj! (
		gm convert !startimageObj! -resize 300x300 +profile "*" !endimageObj!
	)
	if exist !endimageObj! (
		ffmpeg -i !intermediateObj! -i !endimageObj! -c:a copy -map 0 -map 1 -metadata:s:v title="Album cover" -metadata:s:v comment="Cover (Front)" -id3v2_version 3 -write_id3v1 1 !endObj!
	)
)

del !intermediateObj!

ENDLOCAL