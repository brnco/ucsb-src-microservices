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
	CALL :make-broadcast-master
	CALL :make-mp3
	CALL :move-to-repo
	GOTO :eof
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
if not exist !mtdObj! (
	md !scratchDir!
	xcopy !startDir! !scratchDir! /y /i
	del *.* /q
	ping -n 10 127.0.0.1>nul
	rd !startDir!
)
popd
	

ping -n 5 127.0.0.1>nul
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
	ffmpeg -i !broadcastObj! -ac 1 -ar 44100 -af afade=t=in:ss=0:d=2,afade=t=out:st=!fadeoutStart!:d=2 -sample_fmt s16 !processingDir!!broadcastObj!
	::move the processed broadcast master and overwrite the previous broadcast master
	move /y !processingDir!!broadcastObj! !startDir!\!broadcastObj!
)
::delete the txt file with the length string in it
del R:\Cylinders\avlab\_tmpLength.txt
GOTO :eof



:make-mp3
pushd !startDir!
::make an intermediary mp3
ffmpeg -i !broadcastObj! -ar 44100 -ab 320k -f mp3 !intermediateObj!
	
::loop through our metadata object and assign each text instance (between tabs) to a letter, j-m
::stream-copy the intermediary mp3 and insert the metadata into the new one
::we make two files here because I've had errors where RIFF header info is overwritten by ID3 info if transcoding from orig wavs
::in the future too this makes it possible to add image to mp3
for /f "tokens=1-4 delims=	" %%j in (!mtdObj!) do (
	ffmpeg -i !intermediateObj! -c:a copy -metadata title="%%j" -metadata artist="%%k" -metadata album="%%l" -metadata date="%%m" -metadata publisher="UCSB Cylinder Audio Archive" -metadata copyright="2016 The Regents of the University of California" -id3v2_version 3 -write_id3v1 1 !endObj!
)
del !intermediateObj!
popd
GOTO :eof

	
:move-to-repo
::test to find out the directory structure for saved files
if "!cylNum:~0,1!"=="0" (
	set endDir=R:\Cylinders\0000\!cylNum!
	xcopy !startDir! !endDir! /y /i
)
::if first digit more than 0 it enters this condition, and we ask if it's more or less than 10000
if not "!cylNum:~0,1!"=="0" (
	::set vars for cylNum and 10000, to see if greater, convert to numbers from strings
	set /a bar=!cylNum!
	set /a fubar=10000
	if !bar! GTR !fubar! (
		set cylNum_fiveDigit=!cylNum:~0,2!
		set destThousandDir=!cylNum_fiveDigit!000
		set endDir=R:\Cylinders\!destThousandDir!\!cylNum!\
		xcopy !startDir! !endDir! /y /i
	)
	if !bar! LSS !fubar! (
		set cylNum_fourDigit=!cylNum:~0,1!
		set destThousandDir=!cylNum_fourDigit!000
		set endDir=R:\Cylinders\!destThousandDir!\!cylNum!\
		xcopy !startDir! !endDir! /y /i
	)
)

::generate checksums for orig and migrated directories
fsum !startDir! /t:e 
fsum !endDir! /t:e 
pushd !startDir!
::go back into the start directory
for /r %%j in (*.md5) do (
	set startObj=%%j
	::set the drive
	set "d=%%~dj"
	::set the path
	set "p=%%~pj"
	::set a name for this object
	set "n=%%~nj"
	set x=%%~xj
	::set a variable to the .md5 file on the R:\ drive
	set endObj=!endDir!!n!!x!
	::grab the string from the .md5 file in the capture directory
	for /f "tokens=*" %%k in (!startObj!) do (
		set preCopy=%%k
		::grab the string from the .md5 file in the repository directory
		for /f "tokens=*" %%m in (!endObj!) do (
			set postCopy=%%m
			::ask if they are the same string
			if !preCopy!==!postCopy! (
				::if they are, delete the .wav and then delete the .md5
				::this notation works because the MD5 file is "named" name.wav
				::so the .md5 is the extension, and the .wav is part of the "name"
				::but that "name" also corresponds to a file that we can work with
				::i just think that is so cool
				del !d!!p!!n!
				del !d!!p!!n!!x!
			)
		)
	)
)
popd
GOTO :eof

:End

ENDLOCAL
