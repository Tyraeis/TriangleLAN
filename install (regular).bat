@echo off
cd %~dp0
call _copy_files.bat

cd /d "%USERPROFILE%\Desktop\TriangleLAN"
call install-regular.bat