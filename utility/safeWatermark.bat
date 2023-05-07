@echo off
rem initial version made by DevilKkw
setlocal enabledelayedexpansion

rem Set absolute path of your png watermark image,the image must have alpha channale
set "watermarkFile=C:/water.png" 
rem set absolute path for output image, all image with watermark are saved here
set "outputFolder=C:/watermarked"

rem Create the output folder if it doesn't exist
mkdir "%outputFolder%" 2>nul

rem Process each dragged file
for %%F in (%*) do (
    rem Extract the name and extension of the dragged image file
    set "filename=%%~nxF"
    set "extension=%%~xF"

    rem Remove leading and trailing quotes from filename
    set "filename=!filename:"=!"

    rem Display the command being executed
    echo magick "%%~F" "%watermarkFile%" -gravity southeast -compose blend -define compose:args=50 -composite "%outputFolder%\!filename: =!-w!extension!"

    rem Apply watermark using ImageMagick's blend operator with 50% opacity
    magick "%%~F" "%watermarkFile%" -gravity southeast -compose blend -define compose:args=50 -composite "%outputFolder%\!filename: =!-w!extension!"
    echo Watermark applied to "%%~nxF" successfully!
)

endlocal

pause