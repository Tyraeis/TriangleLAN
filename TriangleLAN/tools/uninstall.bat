@echo off
taskkill /f /im "python.exe"
taskkill /f /im "pythonw.exe"
taskkill /f /im "Steam.exe"
timeout /t 5
cd /d "%~dp0\.."
rmdir TriangleLAN /s/q