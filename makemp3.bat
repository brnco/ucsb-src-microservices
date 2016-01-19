@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

set startObj=%1
set mtdDir=%2

::grab filename
set filename=!startObj:~0,-4!

::make sure the path to metadata object is formatted correctly
set _mtd-backslash=!mtdDir:~-1!
if not !_mtd-backslash!==\ (
	set mtdDir=!mtdDir!\
)

::grab metadata object
set mtdObj=!mtdDir!!filename!-mtd.txt
::grab intermediate and end objects
set intermediateObj=!filename!e.mp3
set endObj=!filename!d.mp3

::actually make the thing, takes two passes
ffmpeg -i !startObj! -ar 44100 -ab 320k -f mp3 !intermediateObj!

::if mtdObj exists we'll pop it in there
if exist !mtdObj! (
	for /f "tokens=1-4 delims=	" %%g in (!mtdObj!) do (
		ffmpeg -i !intermediateObj! -c:a copy -metadata title="%%g" -metadata artist="%%h" -metadata album="%%i" -metadata date="%%j" -metadata publisher="UCSB" -metadata copyright="2016 The Regents of the University of California" -id3v2_version 3 -write_id3v1 1 !endObj!
	)
	del !intermediateObj!
)

::if mtdObj doesnt exist just rename what we got
if not exist !mtdObj! (
	ren !intermediateObj! !endObj!
)

ENDLOCAL