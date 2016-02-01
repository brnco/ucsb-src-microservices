::robocopies, hashes the original and robocopy, deletes original if hashes match
::takes 3 arguments for input and output folderpaths which must end with \
::-folder flag indicates folder while inputting filename works for indv files
::use 1 - hashmove blah.txt C:\foo C:\fubar
::use 2 - hashmove -folder C:\foo C:\fubar

@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

::set arguments to vars
set flag=%1
set startDir=%2
set endDir=%3

::check that the inputs are formatted right
set _sd-backslash=!startDir:~-1!
set _ed-backslash=!endDir:~-1!
if not !_sd-backslash!==\ (
	set startDir=!startDir!\
)
if not !_ed-backslash!==\ (
	set endDir=!endDir!\
)

::hashmove for folders
if !flag!==-folder (
	pushd !startDir!
	for /r %%j in (*) do (
		if not %%~xj==.md5 (
			set flag=%%~nj%%~xj
			CALL :hashmovefiles !flag!
		)
	)
	popd
	ping -n 5 127.0.0.1>nul
	rd !startDir!
)

::hashmove for files
::var names get confusing here
if not !flag!==-folder (
	:hashmovefiles
	robocopy !startDir! !endDir! !flag!
	if not exist !startDir!!flag!.md5 (
			fsum !startDir!!flag! !startDir!!flag!.md5 /o
	)
	fsum !endDir!!flag! !endDir!!flag!.md5 /o
	pushd !startDir!
	::loop through the directory we've been working with, and for every .md5 file, compare the string to the .md5 file in the destination
	for /r %%j in (*.md5) do (
		set startObj=%%j
		::set the drive
		set "d=%%~dj"
		::set the path
		set "p=%%~pj"
		::set the name
		set "n=%%~nj"
		::set the extension, which is .md5
		set x=%%~xj
		::set a variable to the .md5 file in the destination folder 
		set endObj=!endDir!!n!!x!
		::grab the string from the .md5 file in the start directory
		for /f "tokens=*" %%k in (!startObj!) do (
			set preCopy=%%k
			::grab the string from the .md5 file in the end directory
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
)
GOTO :eof
popd