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
::send the user a bunch of info on how to set up the system
::there's lots that can go wrong
echo.
echo verify the following EOS Utility preferences:
echo File Name: Shooting Date - Sequential Number
echo no file prefix
echo Number of Digitis 4
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
::if this file already exists it'll enter this loop, print a msg, and exit without doing anything
::this keeps you form accidentally making a dupe
if exist !captureDir!!barcode!.CR2 (
	echo sorry to tell you mate, you've already scanned that barcode
	pause
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

::more error detection, if a files exists here and it's name is the date, we didnt rename it
if exist 2016*.CR2 (
	echo you missed scanning a barcode, sorry to tell you that mate
	pause
)
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