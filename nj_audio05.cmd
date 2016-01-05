::this batch file is for post-processing of audio files for the national jukebox project at UCSB
::here's what it does:
::changes every instance of "ucsb" in \in_process to "cusb" for both files and folders
::takes our intermediate broadcast masters and inserts 2s fade ins and outs, saves them to the broadcast master directory
::generates a checksum, moves, and renames archival master files to a quality control folder
::generates a checksum, moves software-processed broadcast masters to a quality control folder
::BEC20160105

@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

::lets set some paths
::here is the main directory where we do Jukebox work
::end this variable string with a \
set processingMainDir=R:\78rpm\avlab\national_jukebox\in_process\
::here are the subdirectories for individual steps in the process
::they are derived from the workflow of those halcyon pre-script days
::here's where our raw archival masters go
set rawArchDir=!processingMainDir!audio_captures\master-sides\
::here's where our raw broadcast masters go
set rawBroadDir=!processingMainDir!audio_captures\intermediate-sides\
::here's where the broadcast masters go once they've been processed
set processedBroadDir=!processingMainDir!audio_captures\broadcast-sides\
::here is a pre-SIP holding pen for all of these production files
set qualityControlDir=!processingMainDir!pre-ingest-QC\


CALL :rename_ucsbtocusb
CALL :process_intermediates
CALL :move_andRen_archival_toQC
CALL :move_broadcast_toQC
CALL :delete-bs
GOTO :END


:rename_ucsbtocusb
pushd !processingMainDir!audio_captures\
::for files
for /r %%g in ("ucsb*.*") do (
	set name=%%~ng
	set ext=%%~xg
	::do a string substitution, replacing ucsb_ with cusb_
	set newname=!name:ucsb_=cusb_!
	::rename for files takes a full path in the first argument and just a name.extension in the second
	ren "%%g" "!newname!!ext!"
)

::for folders
for /D /r %%g in ("ucsb*") do (
		set name=%%~ng
		set newname=!name:ucsb_=cusb_!
		ren "%%g" "!newname!"
)
popd


:process_intermediates
pushd !rawBroadDir!
::for files rooted at the raw broadcast directory directory that are wavs
for /r %%j in (*.wav) do (
	set "startObj=%%j"
	echo processing !startObj!
	::set the drive
	set "d=%%~dj"
	::set the path
	set "p=%%~pj"
	::set the name
	set "n=%%~nj"
	::set the extension
	set "x=%%~xj"
	::set path for finished file to be saved to
	set "c=!processedBroadDir!"
	::check that this files doesn't already exist in the output drectory
	if not exist !c!!n!!x! (
		::use this ffmpeg extension to port the duration of a wav to a temp text file
		ffprobe -i !d!!p!!n!!x! -show_entries format=duration -v quiet -of csv="p=0" > R:\78rpm\avlab\national_jukebox\_tmpLength.txt
		::loop thru the contents of that file (1 text string)
		for /f "delims=" %%i in (R:\78rpm\avlab\national_jukebox\_tmpLength.txt) do (
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
			ffmpeg -i !d!!p!!n!!x! -ac 1 -ar 44100 -af afade=t=in:ss=0:d=2,afade=t=out:st=!fadeoutStart!:d=2 -sample_fmt s16 !c!!n!!x!
		)
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
	::initialize the object's original name
	set name=%%~nj
	::rename to lc's spec, with an m at the end
	::rename takes full path as first argument, just name as second
	ren %%j !name!m.wav
	::generate a data chunk checksum and embed it into the md5 chunk
	bwfmetaedit --MD5-Embed !rawArchDir!!name!m.wav
	::if the folder doesnt already exist, make it exist
	if not exist !qualityControlDir!!name!\ (
		md !qualityControlDir!!name!\	
	)
	::move the renamed archival master to a QC folder
	move !rawArchDir!!name!m.wav !qualityControlDir!!name!\
	set /a count+=1
	echo !count!
)
popd
GOTO :eof



:move_broadcast_toQC
pushd !processedBroadDir!
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
