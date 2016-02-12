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

::mkae new broadcast master with fades, ID3 tags in processing dir
md processingDir
ffprobe -i !startObj! -show_entries format=duration -v quiet -of csv="p=0" > _tmpLength.txt
::loop thru the contents of that file (1 text string)
for /f "delims=" %%i in (_tmpLength.txt) do (
	set _length=%%i
	::separate decimal values from whole number values because windows
	set decimal=!_length:*.=!
	::as long as wav files are btw 100s - 999s in length, this will return the whole number of seconds of the file
	set _whole=!_length:~0,3!
	::convert that string to a number
	set /a whole=!_whole!
	::subtract 2 from that number to get the whole-number start time of the fade out, fades are 2s long
	set /a _fadeoutStart=!whole!-2
	::recombine the whole-number fadeout start time with the decimal value from earlier and we get a 2s fadeout that ends exactly when the wav ends
	set fadeoutStart=!_fadeoutStart!.!decimal!
	::call ffmpeg with the input, set the audio channel to downmix to 1 (mono), set sample rate to 44100, set the fades, insert calculated start time form earlier, set the sample rate, set the output
	if exist !mtdObj! (
		ffmpeg -i !startObj! -i !mtdObj! -map_metadata 1 -ac 2 -ar 44100 -af afade=t=in:ss=0:d=2,afade=t=out:st=!fadeoutStart!:d=2 -sample_fmt s16 -id3v2_version 3 -write_id3v1 1 %CD%\processingDir\!startObj!
	)
	if not exist !mtdObj! (
		ffmpeg -i !startObj! -ac 2 -ar 44100 -af afade=t=in:ss=0:d=2,afade=t=out:st=!fadeoutStart!:d=2 -sample_fmt s16 -id3v2_version 3 -write_id3v1 1 %CD%\processingDir\!startObj!
	)
	::move the processed broadcast master and overwrite the previous broadcast master
	move /y %CD%\processingDir\!startObj! !startObj!
)
::delete the txt file with the length string in it
del _tmpLength.txt
rd processingDir

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