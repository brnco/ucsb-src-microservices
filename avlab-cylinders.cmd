::post-processing for mass-digitization of cylinders
::takes the broadcast master and makes an intermediary mp3
::takes the intermediary mp3 and makes a final mp3 with ID3 tags
::moves the SIP to the R:\Cylinders share
::checksums orig folder and migrated folder
::if checksums match the files are deleted and the orig capture directory is deleted too
::BEC 20151130

@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

for /f "tokens=*" %%g in ('dir /b /s /a:d /o:n "R:\Cylinders\avlab\audio_captures\*"') do (
	::initialize a bunch of variables
	set startDir=%%g
	set cylNum=%%~ng
	set archObj=cusb-cyl!cylNum!a.wav
	set broadcastObj=cusb-cyl!cylNum!b.wav
	set intermediateObj=cusb-cyl!cylNum!e.mp3
	set endObj=cusb-cyl!cylNum!d.mp3
	set mtdObj=cusb-cyl!cylNum!-mtd.txt
	set processingDir=R:\Cylinders\avlab\audio_captures\!cylNum!\processingDir\
	set scratchDir=T:\avlab\projects\cylinder-scratch\!cylNum!\
	CALL :pre-process-verify
	echo "pre process done"
	CALL :make-broadcast-master
	echo "make broadcast master done"
	CALL :make-mp3
	echo "makemp3 done"
	CALL :move-to-repo
)


:pre-process-verify
::loop through capture directory\cylNum\ and
::initialize a buncha variables and
::verify broadcast and archival masters are present
::verify 
::if not move it to a scratch folder and deal with it later
pushd !startDir!
if not exist !archObj! (
	md !scratchDir!
	xcopy !startDir! !scratchDir! /y /i
	del *.* /q
	ping -n 10 127.0.0.1>nul
	rd !startDir!
)
if not exist !broadcastObj! (
	md !scratchDir!
	xcopy !startDir! !scratchDir! /y /i
	del *.* /q
	ping -n 10 127.0.0.1>nul
	rd !startDir!
)
popd
GOTO :eof

:make-broadcast-master
pushd !startDir!
md !processingDir!
::run this extension on the broadcast master and find where to put the fades
ffprobe -i !broadcastObj! -show_entries format=duration -v quiet -of csv="p=0" > R:\Cylinders\avlab\_tmpLength.txt
::loop thru the contents of that file (1 text string)
for /f "delims=" %%i in (R:\Cylinders\avlab\_tmpLength.txt) do (
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
	ffmpeg -i !broadcastObj! -i !mtdObj! -map_metadata 1 -ac 1 -ar 44100 -af afade=t=in:ss=0:d=2,afade=t=out:st=!fadeoutStart!:d=2 -sample_fmt s16 -id3v2_version 3 -write_id3v1 1 !processingDir!!broadcastObj!
	::move the processed broadcast master and overwrite the previous broadcast master
	move /y !processingDir!!broadcastObj! !startDir!\!broadcastObj!
)
::delete the txt file with the length string in it
del R:\Cylinders\avlab\_tmpLength.txt
rd !processingDir!
popd
GOTO :eof



:make-mp3
pushd !startDir!
ffmpeg -i !broadcastObj! -ar 44100 -ab 320k -f mp3 -id3v2_version 3 -write_id3v1 1 !endObj!
popd 
GOTO :eof

	
:move-to-repo
::test to find out the directory structure for saved files
if "!cylNum:~0,1!"=="0" (
	set endDir=R:\Cylinders\0000\!cylNum!
	hashmove -folder !startDir! !endDir!
)
::if first digit more than 0 it enters this condition, and we ask if it's more or less than 10000
if not "!cylNum:~0,1!"=="0" (
	::set vars for cylNum and 10000, to see if greater, convert to numbers from strings
	set /a bar=!cylNum!
	set /a fubar=10000
	if !bar! GTR !fubar! (
		set cylNum_fiveDigit=!cylNum:~0,2!
		set destThousandDir=!cylNum_fiveDigit!000
		set endDir=R:\Cylinders\!destThousandDir!\!cylNum!
		hashmove -folder !startDir! !endDir!
	)
	if !bar! LSS !fubar! (
		set cylNum_fourDigit=!cylNum:~0,1!
		set destThousandDir=!cylNum_fourDigit!000
		set endDir=R:\Cylinders\!destThousandDir!\!cylNum!
		hashmove -folder !startDir! !endDir!
	)
)
echo Cylinder!cylNum! >> R:/Cylinders/avlab/to-update.txt

GOTO :eof

:End

ENDLOCAL
