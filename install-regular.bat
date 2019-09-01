@echo off
cd /d %~dp0
xcopy TriangleLAN "%USERPROFILE%\Desktop\TriangleLAN" /s/i

cd /d "%USERPROFILE%\Desktop\TriangleLAN"
start "TriangleLAN" install.bat