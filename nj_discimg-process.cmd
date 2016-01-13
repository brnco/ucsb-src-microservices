@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

set intermediatesDir=R:\78rpm\avlab\national_jukebox\in_process\visual_captures\intermediates\
set outputDir=R:\78rpm\avlab\national_jukebox\in_process\visual_captures\processed\

pushd !intermediatesDir!
for /r %%g in (*.DNG) do (
	set startObj=%%g
	set barcode=%%~ng
	echo processing !barcode!
	gm convert !startObj! -crop 3648x3648+920 -rotate 180 !outputDir!!barcode!.tif
)
popd
ENDLOCAL