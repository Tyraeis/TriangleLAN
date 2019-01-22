@echo off
cd %~dp0
call _copy_files.bat
xcopy TriangleLAN\archives "%USERPROFILE%\Desktop\TriangleLAN\archives" /s /i

cd /d "%USERPROFILE%\Desktop\TriangleLAN"
call install-regular.bat