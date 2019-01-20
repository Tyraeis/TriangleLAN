cd %~dp0
_copy_files.bat
xcopy TriangleLAN\archives %USERPROFILE%\Desktop\TriangleLAN\archives /s

cd %USERPROFILE%\Desktop\TriangleLAN
start "" "install (admin).bat"