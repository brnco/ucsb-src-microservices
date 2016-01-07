::this file is used for the quality control of pre-SIPs for UCSB as part of the National Jukebox Project
::it loops through the directories in our quality-control purgatory folder and see if all the files are in there
::then, if a folder has the three key files, tifs and both wavs, it moves them to our pre-finished directory, where we keep 1000 files at a time to ship to LoC
::BEC 20160107

@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

set qcPath=R:\78rpm\avlab\national_jukebox\in_process\pre-ingest-QC\
set workingSIP=R:\78rpm\avlab\national_jukebox\in_process\11000\
::loop through the folders in our QC directory
for /f "tokens=*" %%g in ('dir /b /s /a:d /o:n "!qcPath!*"') do (
	
	set startDir=%%g
	set barcode=%%~ng
	echo Processing !barcode!
	set endDir=!workingSIP!!barcode!\
	::set variables to the paths and names of the files inside
	set "tof=!qcPath!!barcode!\!barcode!.tif"
	set "mwav=!qcPath!!barcode!\!barcode!m.wav"
	set "cwav=!qcPath!!barcode!\!barcode!.wav"
	::if we have already made this directory, that's an error we gotta look into
	if exist !endDir! (
		echo check on !barcode!
	)
	::if the master wavs exist	
	if exist !mwav! (
		::if the broadcast wavs exist
		if exist !cwav! (
			::if the tifs exist
			if exist !tof! (
				::here is a directory with all of the files that we need to submit to lc
				echo !barcode! >> t:\avlab\national_jukebox\in_process\nj_toQC-logs\fin_%DATE%.txt
				::make sure you're not about to replace a directory we've already worked on
				if not exist !endDir! (
					::ok so if we've made it this far it means everything we want to exist extists and we can pop it into our working repo directory
					md !endDir!
					xcopy /y !startDir! !endDir!
					fsum !startDir! /t:e 
					fsum !endDir! /t:e 
					pushd !startDir!
					::go back into the start directory
					::loop through all the checksums
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
				)
			)
		)
	)
	ping -n 3 127.0.0.1>nul
	rd !startDir!
)
ENDLOCAL
