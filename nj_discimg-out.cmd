::this batch file is for post-processing of image files for the national jukebox project at UCSB
::it moves the original disc images (CR2), production masters (DNG), and access derivatives (TIF) to quality control folders

@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

::set a bunch of paths up front
::here is the main production directory for our Jukebox stuff
set mainWorkingDir=R:\78rpm\avlab\national_jukebox\in_process\visual_captures\
::here are individual directories for our various filetypes
set cr2Dir=!mainWorkingDir!raw-captures
::we needed a separate directory for the dng files because of stupid photoshop
set dngDir=!mainWorkingDir!intermediates\
::we needed a separate directory for the tif files also because of stupid photoshop
set tifDir=!mainWorkingDir!ps-processed\
::here is our destination directory
set qualityControlDir=R:\78rpm\avlab\national_jukebox\in_process\pre-ingest-QC\

CALL :rename_ucsbtocusb
CALL :move_cr2_to_toQC
CALL :move_dng_to_toQC
CALL :move_tif_to_toQC

GOTO :End

:rename_ucsbtocusb
::just double checking that this has happened
pushd !mainWorkingDir!
::for files
for /r %%g in ("ucsb*.*") do (
	set name=%%~ng
	set ext=%%~xg
	::do a string substitution, replacing ucsb_ with cusb_
	set newname=!name:ucsb_=cusb_!
	::rename for files takes a full path in the first argument and just a name.extension in the second
	ren "%%g" "!newname!!ext!"
		)
	)
::for folders
for /D /r %%g in ("ucsb*") do (
		set name=%%~ng
		set newname=!name:ucsb_=cusb_!
		ren "%%g" "!newname!"
		)
	)
popd



:move_cr2_to_toQC
::get us into the directory with the camera raw files and loop through each one
pushd !cr2Dir!
for /r %%j in (*.cr2) do (
	::set the name
	set name=%%~nj
	::ask if that folder already exists in our qc folder, and if it doesn't, make it
	if not exist !qualityControlDir!!name!\ (
		md !qualityControlDir!!name!\ 
	)
	::move our cr2 file to our quality control directory in a folder with its name
	move %%j !qualityControlDir!!name!
)
popd
GOTO :eof

:move_dng_to_toQC
pushd !dngDir!
for /r %%j in (*.dng) do (
	set name=%%~nj
	if not exist !qualityControlDir!!name!\ (
		md !qualityControlDir!!name!\ 
	)
	move %%j !qualityControlDir!!name!
)
popd
GOTO :eof

:move_tif_to_toQC
pushd !tifDir!
for /r %%j in (*.tif) do (
	set name=%%~nj
	if not exist !qualityControlDir!!name!\ (
		md !qualityControlDir!!name!\ 
	)
	move %%j !qualityControlDir!!name!\
)
popd
GOTO :eof

ENDLCOAL

:End