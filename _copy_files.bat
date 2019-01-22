@echo off
cd %~dp0
xcopy TriangleLAN "%USERPROFILE%\Desktop\TriangleLAN" /i
xcopy TriangleLAN\python "%USERPROFILE%\Desktop\TriangleLAN\python" /s /i
xcopy TriangleLAN\tools "%USERPROFILE%\Desktop\TriangleLAN\tools" /i