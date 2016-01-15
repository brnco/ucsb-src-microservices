::this batch file is for processing files for the avlab's mass digitization efforts at UCSB
::here's what it does:
::moves folder by folder through our capture directory
::splits wav files that are larger than 2GB into multiple parts and deletes the original transfer
::if a file is less than 2GB it doesn't split/ delete
::embeds checksums in whatever wav files are in the containing folder (data chunk only)
::moves the folder to the R:\ drive
::runs whole-file checksums against each file in the containing folder
::for both the file in the capture directory and the one we copied to the r:\ drive
::this verifies that the copy was completed correctly
::if the sums match, we delete the files in the capture directory
::on exit, the script deletes all of the empty directories in the capture directory
::BEC20150624

@echo off


::first, let's delete some garbage files in the capture directory
DEL /S "H:\new_ingest\*.gpk"
DEL /S "H:\new_ingest\*.mrk"

::this allows us to run our loops they way we want to
SETLOCAL ENABLEDELAYEDEXPANSION

::here is the start of our shell
::this section controls the behaviour of the script, the section following that controls the processing of each file
::you could consider this an int main{} if you wanted to
::if the capture directory ever changes the only thing you need to change in this script is the dir in this loop
::every other directory designation is referenced to the dir in this loop

::loop through capture directory, folder by folder
for /f "tokens=*" %%g in ('dir /b /s /a:d /o:n "H:\new_ingest\*"') do (
	::set the starting directory as a global variable. put a \ at the end so that it's more useful as a path
	set "startDir=%%g\"
	::set the name, equivalent to our "audio number" or accession number
	set "audioNumber=%%~ng"
	::ask the user if they want to continue running the script, run automatically if they don't respond
	::this allows users to stop the script after each folder is done being processed, which could otherwise delay their work
	echo 1. To continue press 1, ~or do nothing~
	echo 2. To stop this process now, press 2
	CHOICE /C 12 /T 5 /D 1 /M "What would you like to do?"
	IF errorlevel 2 GOTO bye
	IF errorlevel 1 CALL :wav-process-shell
)

:bye
::one cool thing is that this script reads h:\new_ingest in numerical order
::so if we know the last directory to be processed, we know we can delete every directory before it because they're safely on the server
::by "in order" I of course mean "in windows order" which is dumb: a1300 comes before a220, for example
::probably best to double check before doing that tho :)
for /f "tokens=*" %%g in ('dir /b /s /a:d /o:n "H:\new_ingest\*"') do (
	rd %%g
)
Exit /b



:wav-process-shell
CALL :split
CALL :embed
CALL :move
CALL :verify
GOTO :eof



:split
pushd !startDir!
echo processing !startDir!
::let's make a log on the desktop of the files that we process in this session eh?
::echo !startDir! >> C:\Users\specpa7\Desktop\lab-transfers-%date%.txt
::so, we're in a folder already and now we're going to apply an operation to each wav file in that folder
for /r %%j in (*.wav) do (
	::initialize a ton of strings
	set "startObj=%%j"
	::set the drive
	set "d=%%~dj"
	::set the path
	set "p=%%~pj"
	::set a name for this object
	set "n=%%~nj"
	::set the extensions, one with the use char
	set "x=.wav"
	set "xa=a.wav"
	::this is the actual name of our audio objects
	set "v=cusb-!audioNumber!"
	::here is the name of our audio objects if they have faces, like for open reel tapes
	set faceA=!v!Aa
	set faceB=!v!Ba
	if !n! == !faceA! echo we have a faceA
	if !n! == !faceB! echo we have a faceB
	::this subroutine determines the pre-ingest processing needs of a particular file
	::use this ffmpeg utility to print the length of the file, in seconds, to a txt file
	ffprobe -i !startObj! -show_entries format=duration -v quiet -of csv="p=0" > H:\_tmpLength.txt
	::use this same ffmpeg utility to determine if an object is mono or stereo
	ffprobe -i !startObj! -show_entries stream=channels -v quiet -of csv="p=0" > H:\_tmpChannel.txt
	::loop thru the 1 value in this text file, separate the number of channels, a string variable, from the rest of the string
	for /f "delims=" %%g in (H:\_tmpChannel.txt) do (
		::set some numeric variables that we can later use to run a comparison
		set /a chanConfig=%%g
		set /a mono=1
		set /a stereo=2
		::debug
		echo number of channels=!chanConfig!
		::this next bit actually does the processing
		::if stereo, the file has to be split at 1hr intervals to stay within the 2GB wav spec
		::if mono, the file has to be split at 2hr intervals to stay within the 2GB wav spec
		::if the channel configuration equals stereo the object enters this loop
		if !chanConfig! EQU !stereo! (
			for /f "delims=" %%i in (H:\_tmpLength.txt) do (
				::initialize this variable for number of seconds in one and two hours
				set /a oneHr=3600
				set /a twoHr=7200
				::set the length variable, a string at this point, representing the length in s of the audio file, to the one line in the txt file
				set length=%%i
				::separate the length of the file into just its whole number of seconds, because fuckinwndows can't deal w/ floating point numbers
				for /f "tokens=1 delims=." %%a in ("!length!") do (
					set /a len=%%a
				)
				::compare the number of seconds in the file to the number of seconds in two hours
				::ffmpeg is really bad at dealing with mixed strings and variables so
				::for the variable notation at the end, its the drive letter ~d, path ~p, name ~v, and segment -00
				if !len! GTR !twoHr! (
					if !n! == !faceA! (
						echo stereo, bigger than two hours, faceA
						ffmpeg -i !startObj! -y -acodec copy -ss 00:00:00 -t 01:00:00 !d!!p!!v!A-01a.wav
						ffmpeg -i !startObj! -y -acodec copy -ss 01:00:00 -t 02:00:00 !d!!p!!v!A-02a.wav
						ffmpeg -i !startObj! -y -acodec copy -ss 02:00:00 -t 03:00:00 !d!!p!!v!A-03a.wav
					)
					if !n! == !faceB! (
						echo stereo, bigger than two hours, faceB
						ffmpeg -i !startObj! -y -acodec copy -ss 00:00:00 -t 01:00:00 !d!!p!!v!B-01a.wav
						ffmpeg -i !startObj! -y -acodec copy -ss 01:00:00 -t 02:00:00 !d!!p!!v!B-02a.wav
						ffmpeg -i !startObj! -y -acodec copy -ss 02:00:00 -t 03:00:00 !d!!p!!v!B-03a.wav
					)
					if not !n! == !faceB! (
						if not !n! == !faceB! (
							echo stereo, bigger than two hours, no face
							ffmpeg -i !startObj! -y -acodec copy -ss 00:00:00 -t 01:00:00 !d!!p!!v!-01a.wav
							ffmpeg -i !startObj! -y -acodec copy -ss 01:00:00 -t 02:00:00 !d!!p!!v!-02a.wav
							ffmpeg -i !startObj! -y -acodec copy -ss 02:00:00 -t 03:00:00 !d!!p!!v!-03a.wav
						)
					)
					del !startObj!
				)
				::compare the number of seconds in the file to the number of seconds in one hour
				if !len! GTR !oneHr! (
					if !n! == !faceA! (
						echo stereo, bigger than one hour, faceA
						ffmpeg -i !startObj! -y -acodec copy -ss 00:00:00 -t 01:00:00 !d!!p!!v!A-01a.wav
						ffmpeg -i !startObj! -y -acodec copy -ss 01:00:00 -t 02:00:00 !d!!p!!v!A-02a.wav
					)
					if !n! == !faceB! (
						echo stereo, bigger than one hour, faceB
						ffmpeg -i !startObj! -y -acodec copy -ss 00:00:00 -t 01:00:00 !d!!p!!v!B-01a.wav
						ffmpeg -i !startObj! -y -acodec copy -ss 01:00:00 -t 02:00:00 !d!!p!!v!B-02a.wav
					)
					if not !n! == !faceB! (
						if not !n! == !faceA! (
							echo stereo, bigger than one hour, no face
							ffmpeg -i !startObj! -y -acodec copy -ss 00:00:00 -t 01:00:00 !d!!p!!v!-01a.wav
							ffmpeg -i !startObj! -y -acodec copy -ss 01:00:00 -t 02:00:00 !d!!p!!v!-02a.wav
						)
					)
					del !startObj!
				)
			)
		)
		::if the channel configuration equals mono we enter this loop
		if !chanConfig! EQU !mono! (
			for /f "delims=" %%i in (H:\_tmpLength.txt) do (
				::initialize this variable for number of seconds in two hours
				set /a twoHr=7200
				::set the length variable, a string at this point, representing the length in s of the audio file, to the one line in the txt file
				set length=%%i
				::separate the length of the file into just its whole number of seconds, because fuckinwndows
				for /f "tokens=1 delims=." %%a in ("!length!") do (
					set /a len=%%a
				)
				::compare the number of seconds in the file to the number of seconds in two hours
				::ffmpeg is really bad at dealing with mixed strings and variables so
				::for the variable notation at the end, its the drive letter ~d, path ~p, name ~n, and segment -00
				if !len! GTR !twoHr! (
					if !n! == !faceA! (
						echo mono, bigger than two hours, faceA
						ffmpeg -i !startObj! -y -acodec copy -ss 00:00:00 -t 02:00:00 !d!!p!!v!A-01a.wav
						ffmpeg -i !startObj! -y -acodec copy -ss 02:00:00 -t 04:00:00 !d!!p!!v!A-02a.wav
					)
					if !n! == !faceB! (
						echo stereo, bigger than two hours, faceB
						ffmpeg -i !startObj! -y -acodec copy -ss 00:00:00 -t 02:00:00 !d!!p!!v!B-01a.wav
						ffmpeg -i !startObj! -y -acodec copy -ss 02:00:00 -t 04:00:00 !d!!p!!v!B-02a.wav
					)
					if not !n! == !faceB! (
						if not !n! == !faceA! (
							echo stereo, bigger than two hours, no face
							ffmpeg -i !startObj! -y -acodec copy -ss 00:00:00 -t 02:00:00 !d!!p!!v!-01a.wav
							ffmpeg -i !startObj! -y -acodec copy -ss 02:00:00 -t 04:00:00 !d!!p!!v!-02a.wav
						)
					)
					del !startObj!
				)
			)
		)
	)
)
	
::delete the txt files
del H:\_tmpLength.txt
del H:\_tmpChannel.txt
popd
GOTO :eof




:embed
pushd !startDir!
::add BEXT metadata
echo embedding BEXT metadata
echo embedding data chunk checksums...
for /r %%j in (*.wav) do (
	::initialize a ton of strings
	set "startObj=%%j"
	::set the drive
	set "d=%%~dj"
	::set the path
	set "p=%%~pj"
	::set a name for this object
	set "n=%%~nj"
	::set the extensions, one with the use char
	set "x=.wav"
	set "xa=a.wav"
	::this var comes in handy i promise
	set "v=cusb-!audioNumber!"
	::set a variable to the metadata file we exported from FM when we clicked "New Master"
	set "mtd=!d!!p!!audioNumber!metadata.tab"
	::check to see if the metadata file exists and if it doesn't oh well
	if exist !mtd! (
		::loop through the tab-separated elements of this text file
		::note, that space after "delims" is irl a TAB literal. if this isn't working try typing into CLI: cmd /f:off
		for /f "tokens=1-6 delims=	" %%k in (!mtd!) do (
			::the real key- these values must match the order of the entries in the tab file
			::these variable names derived from their respective field names in FM
			set wave=!startObj!
			set "originator=US,CUSB,SPECCOLL"
			set tapeNo=%%k
			set mastered=%%l
			set masterKey=%%m
			set tapeTitle=%%n
			set mssNo=%%o
			set collName=%%p
			::this is for debugging
			echo tapeNo=!tapeNo!
			echo mssNo=!mssNo!
			echo collName=!collName!
			echo tapeTitle=!tapeTitle!
			echo masterKey=!masterKey!
			echo mastered=!mastered!
			::gotta do some string transformations to get the date into a format that bwfmetaedit likes
			::can't be exported from FM in this form
			for /f "tokens=1,2,3 delims=/" %%q in ("!mastered!") do (
				set month=%%q
				set day=%%r
				set year=%%s
				set yyyymmdd=!year!-!month!-!day!
			)
			::we get 256 chars for this bext field so might as well use em
			set description=--tapeNumber-!tapeNo! --mssNo-!mssNo! --collection-!collName! --tapeTitle-!tapeTitle! --masterKey-!masterKey!
			set originatorRef=cusb-a!tapeNo!
			
			::standard for bwfmetaedit, key name followed by text. description needs quotes around it to deal with spaces
			bwfmetaedit --Originator=!originator! --Description="!description!" --originatorReference=!originatorRef! !wave!
		)
	)
	::add_md5checksum
	bwfmetaedit --MD5-Embed-Overwrite !startObj!
)
popd
GOTO :eof




:move
::move_fromNewIngest-toR
echo moving !audioNumber!
::gonna do some string separation
set foo=!audioNumber!
::separate just the numeric characters from the audio number
set audioNo=!foo:a=!
set _test=!audioNo!
::if the audionumber is below 1000 its gonna have a leading zero which means we gotta deal with it a little differently
::compare first character in _test to 0 if it's a match copy the folder to the zero folder on R:\
if "!_test:~0,1!"=="0" (
	set dest=R:\audio\0000\!foo!\
	xcopy /y H:\new_ingest\!foo!\* R:\audio\0000\!foo!\ /s /i
)
::if the first digit of the audionumber is above 0 it will fail the previous condition but will enter this one
::figure out if it's a 4 or 5-digit audio number so that we can sort it properly in the R:\ drive
::convert to a number from a string and compare the numbers using greater than or less than
if not "!_test:~0,1!"=="0" (
	set /a bar=audioNo
	set /a fubar=10000
	if !bar! GTR !fubar! (
		set audioNoPref5=!audioNo:~0,2!000
		set dest=R:\audio\!audioNoPref5!\!foo!\
		::this moves the whole folder
		::/y suppresses overwrite prompt
		::/s copies all folders and subfolders
		::/i assumes that target is a directory. good to add trailing / to target as well
		xcopy /y H:\new_ingest\!foo!\* R:\audio\!audioNoPref5!\!foo!\ /s /i
	)
	if !bar! LSS !fubar! (
		set audioNoPref4=!audioNo:~0,1!000
		set dest=R:\audio\!audioNoPref4!\!foo!\
		xcopy /y H:\new_ingest\!foo!\* R:\audio\!audioNoPref4!\!foo!\ /s /i
	)
)

GOTO :eof


:verify
echo verifying transfer, generating whole file checksums
::use FastSum to write whole-file checksums for every object in the folder (that's what the /t:e does)
fsum !startDir! /t:e /o
fsum !dest! /t:e /o

pushd !startDir!
::loop through the directory we've been working with, and for every .md5 file, compare the string to the .md5 file on the r:\ drive
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
	set endObj=!dest!!n!!x!
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
set "var2=!startObj!"
GOTO :eof

ENDLOCAL