

@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

::lets set some paths
::here is the main directory where we do Jukebox work
::end this variable string with a \
set processingMainDir=R:\78rpm\avlab\new_ingest\
::here are the subdirectories for individual steps in the process
::they are derived from the workflow of those halcyon pre-script days
::here's where our raw archival masters go
set rawArchDir=!processingMainDir!audio_captures\master-sides\
::here's where our raw broadcast masters go
set rawBroadDir=!processingMainDir!audio_captures\broadcast-sides\
::here is a pre-SIP holding pen for all of these production files
set qualityControlDir=!processingMainDir!pre-ingest-qc\

CALL S:\avlab\microservices\rename_ucsbtocusb.cmd !processingMainDir!
CALL :process_intermediates
CALL :move_andRen_archival_toQC
CALL :move_broadcast_toQC
CALL :delete-bs
GOTO :END





:process_intermediates
echo back again
pause
pushd !rawBroadDir!
::for files rooted at the raw broadcast directory directory that are wavs
for /r %%j in (*.wav) do (
	set "startObj=%%j"
	echo processing %%~nj
	::set the drive
	set "d=%%~dj"
	::set the path
	set "p=%%~pj"
	::set the name
	set "n=%%~nj"
	::set the extension
	set "x=%%~xj"
	::set path for finished file to be saved to
	set processingDir=!rawBroadDir!!n!\
	::check that this files doesn't already exist in the output drectory
	if not exist !qualityControlDir!!n!\!n!!x! (
		md !processingDir!
		::use this ffmpeg extension to port the duration of a wav to a temp text file
		ffprobe -i !d!!p!!n!!x! -show_entries format=duration -v quiet -of csv="p=0" > R:\78rpm\avlab\new_ingest\_tmpLength.txt
		::loop thru the contents of that file (1 text string)
		for /f "delims=" %%i in (R:\78rpm\avlab\new_ingest\_tmpLength.txt) do (
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
			ffmpeg -i !d!!p!!n!!x! -ar 96000 -ac 2 -af afade=t=in:ss=0:d=2,afade=t=out:st=!fadeoutStart!:d=2 -acodec pcm_s24le !processingDir!!n!!x!
		)
		::move the processed broadcast master to the broadcast master directory, overwriting the raw broadcast master
		move /y !processingDir!!n!!x! !rawBroadDir!!n!!x!
		::delete the processing directory
		rd !processingDir!
		::delete the text file
		del R:\78rpm\avlab\new_ingest\_tmpLength.txt
	)
)
popd
GOTO :eof


:move_andRen_archival_toQC
pushd !rawArchDir!
::initialize a variable so you know how long it'll take
set /a count=0
::for files rooted at the a-side directory that are wavs
for /r %%j in (*.wav) do (
	set name=%%~nj
	set qcNamedDir=!qualityControlDir!!name!\
	::generate a data chunk checksum and embed it into the md5 chunk
	bwfmetaedit --MD5-Embed %%j
	::if the folder doesnt already exist, make it exist
	if not exist !qcNamedDir! (
		md !qcNamedDir!	
	)
	::move the renamed archival master to a QC folder
	move %%j !qcNamedDir!
	ren !qcNamedDir!\!name!.wav !name!a.wav
	set /a count+=1
	echo !count!
)
popd
GOTO :eof



:move_broadcast_toQC
pushd !rawBroadDir!
for /R %%j in (*.wav) do (
	set name=%%~nj
	set qcNamedDir=!qualityControlDir!!name!\
	::generate a checksum and embed it into the md5 chunk
	bwfmetaedit --MD5-Embed %%j
	::if the folder doesnt already exist make it exist
	::move can only move to pre-existing locations
	if not exist !qcNamedDir! (
		md !qcNamedDir!
	)
	move %%j !qcNamedDir!
	ren !qcNamedDir!!name!.wav !name!b.wav
)
popd
GOTO :eof

:delete-bs
pushd !rawArchDir!
for /r %%g in (*.gpk) do del %%g
for /r %%g in (*.bak) do del %%g
for /r %%g in (*.mrk) do del %%g
popd
pushd !processedBroadDir!
for /r %%g in (*.gpk) do del %%g
for /r %%g in (*.bak) do del %%g
for /r %%g in (*.mrk) do del %%g
popd
pushd !rawBroadDir!
for /r %%g in (*.gpk) do del %%g
for /r %%g in (*.bak) do del %%g
for /r %%g in (*.mrk) do del %%g
popd
GOTO :eof

:End


ENDLOCAL
