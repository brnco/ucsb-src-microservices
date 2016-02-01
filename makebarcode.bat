::makebarcode
::take inputs of song name and desried barcode
::outputs barcode file
@echo off

set /p title="Title: "
set /p barcode="Barcode: "

echo.
echo Title: %title%
echo barcode: %barcode%