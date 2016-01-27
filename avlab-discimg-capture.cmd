::this is a workflow-mgmt batch file for capturing disc images in bulk
::the way it works is
::there's an initialization of a capture directory, based on today's date
::then, for each side of each disc
::take a picture of the disc
::wait for it to dl into the capture directory
::scan the barcode
::and the batch file renames it automatically
::there's even error detection because I care about you
::it's gonna be real helpful to have the capture dir open in a window's explorer window while taking pix
::also you can switch quickly btw EOS Utility and CMD by using Alt+Tab
::see bottom of file for overly specific workflow
::BEC20150910

@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

::initialize the date in a way that is useful
set /p dat3=What is today's date (YYYY-MM-DD):%=%
::set the capture directory based on the date
set captureDir=R:\78rpm\avlab\new_ingest\visual_captures\raw-captures\!dat3!\
::make it on the hard drive if it isn't there already
md !captureDir!
::initialize a variable that we'll use to rename the files
set /a count=1
::send the user a bunch of info on how to set up the system
::there's lots that can go wrong
echo.
echo verify the following EOS Utility preferences:
echo File Name: Shooting Date - Sequential Number
echo no file prefix
echo Number of Digitis 4
echo Start 1
choice /M "Did you double check that the count starts at 1"
echo verify the example filename at the bottom of the preferences window
echo.
echo Destination Folder: R:\78rpm\avlab\new_ingest\visual-captures\raw-captures\
echo Subfolder: Shooting date (YYYY-MM-DD) Delimiter: Hyphen
echo verify the example directory and subdir at the bottom of the window
echo.
pushd !captureDir!
GOTO :scanning

:scanning
::scan the barcode
set /p barcode=Scan barcode:%=%
::the camera creates barcodes that look like 2050902-0001 or 20150902-0101
::so to create those filenames we have to use a bunch of IF statements
::first ten files will enter this condition
if !count! LSS 10 (
	::generate a filename for file coming out of camera
	set strCount9=!dat3!-000!count!
	set targetObj=!strCount9!.CR2
	::display the filename next to the scanned barcode for visual qc goodness
	echo raw filename:!strCount9!
	echo.
	echo !targetObj!
	echo %CD%
	rename !targetObj! !barcode!.cr2
	
	if !errorlevel! EQU 1 (
		echo there was a problem with that barcode check it out
		echo.
		::this next goto loops back to the beginning of the sequence
		::by skipping the next two steps in the sequence, which
		::prints the filename and count to a log file
		::iterates the count
		::we keep our raw file names
		::and our expected/ generated file names
		::from getting out of sync
		echo in if
		goto :scanning
	)
	echo !barcode!	!strCount9! >> !captureDir!\!dat3!.txt
)
::files 10-99 go thru this condition
if !count! GEQ 10 (
	if !count! LSS 100 (
		set strCount99=!dat3!-00!count!
		set targetObj=!strCount99!.cr2
		echo raw filename:!strCount99!
		echo.
		rename !targetObj! !barcode!.cr2
		if !errorlevel! EQU 1 (
			echo there was a problem with that barcode check it out
			echo.
			goto :scanning
		)
		echo !barcode!	!strCount99! >> !captureDir!\!dat3!.txt
	)
)
::files 100-999 go thru this condition
if !count! GEQ 100 (
	if !count! LSS 1000 (
		set strCount999=!dat3!-0!count!
		set targetObj=!strCount999!.cr2
		echo raw filename!strCount999!
		echo.
		rename !targetObj! !barcode!.cr2
		if !errorlevel! EQU 1 (
			echo there was a problem with that barcode check it out
			echo.
			goto :scanning
		)
		echo !barcode!	!strCount999! >> !captureDir!\!dat3!.txt
	)
)

set /a count=!count!+1
CALL :scanning
popd
ENDLOCAL

::here's exactly the repetitive motion you'll wanna do
::start with EOS util open
::adjust record on platter
::press space bar to take a picture
::alt+tab to switch to cmd window
::scan barcode
::verify filename in open windows explorer window
::alt+tab to switch back to EOS util
::adjust record on platter
::and so on