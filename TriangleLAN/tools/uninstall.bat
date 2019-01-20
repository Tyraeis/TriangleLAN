taskkill /f /im "python.exe"
taskkill /f /im "pythonw.exe"
timeout /t 5
rmdir "%~dp0" /s/q