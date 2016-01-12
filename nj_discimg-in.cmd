::this is a workflow-mgmt batch file for capturing disc images in bulk for the National Jukebox project at UCSB
::the way it works is
::there's an initialization of a capture directory, based on today's date
::then, for each side of each disc
::scan the barcode into filemaker
::take a picture of the disc
::wait for it to dl into the capture directory
::scan the barcode
::and the batch file renames it automatically
::there's even error detection because I care about you
::it's gonna be real helpful to have the capture dir open in a window's explorer window while taking pix
::also you can switch quickly btw EOS Utility and FM by using Alt+Tab
::BEC20150910

@echo off
SETLOCAL ENABLEDELAYEDEXPANSION
::initialize our directories
::end these strings with \
set filemakerExportDir=C:\Users\specpa7\Desktop\discimg-in-txt\
set captureDir=R:\78rpm\avlab\national_jukebox\in_process\visual_captures\raw-captures\%date%\

pushd !filemakerExportDir!
::there should only be 1 text file in this dir at a time so loop through them
for /r %%g in (*.txt) do (
	::initialize the variable to the name of the text file that FM exported
	set _barcode=%%~ng
	::do a lil string substitution to change ucsb to cusb
	set barcode=!_barcode:ucsb_=cusb_!
	::if this file already exists it'll enter this loop, print a msg, and exit without doing anything
	::this keeps you form accidentally making a dupe
	if exist !captureDir!!barcode!.CR2 (
		echo sorry to tell you mate, you've already scanned that barcode
		pause
		del *.txt
		exit /b
	)
	::this for loop creates a set for all files in the capture dir and sorts by creation date
	::the most recent, the one just in from the camera, is set as our target object
	for /f "tokens=*" %%i in ('dir /o:d /b "!captureDir!*"') do (
		set newest=%%i
		set targetObj=!captureDir!!newest!
	)
	::rename takes a full path and a name.ext
	ren !targetObj! !barcode!.CR2
	::here's some more error detection that checks if there was an error renaming that file
	::if this wasn't here the cmd window would just exit out without telling you anything
	if !errorlevel! EQU 1 (
		echo there was a problem with that barcode check it out
		pause
	)
)
::delete every text file in our filemaker discimg-in dir
del *.txt
popd
::here's where we error check the capture dir
pushd !captureDir!
for /r %%g in (*) do (
	set name=%%~ng
	set dat3=%date%
	set foo=!name:~0,10!
	::this reads
	::if the first 10 digits of the filename are today's date
	if "!name:~0,10!"=="!dat3!" (
		echo you missed scanning a barcode, sorry to tell you that mate
		pause
	)
)
popd
ENDLOCAL