::rename everything in a directory from ucsb to cusb
::the result of a programming error years ago :)
@echo off
SETLOCAL ENABLEDELAYEDEXPANSION
pushd %1
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
ENDLOCAL