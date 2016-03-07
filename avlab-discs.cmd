::processes discs for the AVLAB at UCSB

@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

::lets set some paths
::here is the main directory where we do work
::end this variable string with a \
set processingMainDir=R:\78rpm\avlab\new_ingest\
::here are the subdirectories for individual workflow steps
::here's where our raw archival masters go
set rawArchDir=!processingMainDir!audio_captures\master-sides\
::here's where our raw broadcast masters go
set rawBroadDir=!processingMainDir!audio_captures\broadcast-sides\
::here is a pre-SIP holding pen for all of these production files
set qualityControlDir=!processingMainDir!pre-ingest-qc\

CALL S:\avlab\microservices\rename_ucsbtocusb.cmd !processingMainDir!
CALL :delete-bs
CALL :process_intermediates
CALL :makemp3s
CALL :put_broadcast_inQC
CALL :put_mp3_inQC
CALL ::put_andRen_archival_inQC



GOTO :END

:delete-bs
pushd !rawArchDir!
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


:process_intermediates
pushd !rawBroadDir!
::for files rooted at the raw broadcast directory directory that are wavs
for /r %%j in (*.wav) do (
	echo processing %%~nj
	CALL makebroadcast %%~nj%%~xj
	::rename our newly minted broadcast master with a use character to reflect that
	ren %%j %%~njb%%~xj
)
popd
GOTO :eof

:makemp3s
pushd !rawBroadDir!
for /r %%j in (*b.wav) do (
	CALL makemp3 %%~nj%%~xj
)
popd

:put_broadcast_inQC
pushd !rawbroadDir!
for /R %%j in (*.wav) do (
	set _name=%%~nj%%~xj
	set name=!_name:b.wav=!
	set qcNamedDir=!qualityControlDir!!name!\
	::generate a checksum and embed it into the md5 chunk
	bwfmetaedit --MD5-Embed !_name!
	::if the folder doesnt already exist make it exist
	::move can only move to pre-existing locations
	if not exist !qcNamedDir! (
		md !qcNamedDir!
	)
	CALL hashmove !_name! !rawBroadDir! !qcNamedDir!
)
popd
GOTO :eof



:put_mp3_inQC
pushd !rawBroadDir!
for /R %%j in (*.mp3) do (
	set _name=%%~nj%%~xj
	set name=!_name:d.mp3=!
	set qcNamedDir=!qualityControlDir!!name!\
	::if the folder doesnt already exist make it exist
	::move can only move to pre-existing locations
	if not exist !qcNamedDir! (
		md !qcNamedDir!
	)
	CALL hashmove !_name! !rawBroadDir! !qcNamedDir!
)
popd
GOTO :eof


:put_andRen_archival_inQC
pushd !rawArchDir!
for /R %%j in (*.wav) do (
	set _name=%%~nj
	set name=!_name!a!x!
	ren %%j !name!
	set qcNamedDir=!qualityControlDir!!_name!\
	::generate a checksum and embed it into the md5 chunk
	bwfmetaedit --MD5-Embed !name!
	::if the folder doesnt already exist make it exist
	::move can only move to pre-existing locations
	if not exist !qcNamedDir! (
		md !qcNamedDir!
	)
	CALL hashmove !name! !rawArchDir! !qcNamedDir!
)
popd
GOTO :eof







:End


ENDLOCAL
