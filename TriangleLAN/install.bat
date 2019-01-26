@echo off
cd /d %~dp0
start "TriangleLAN Installer" python/pythonw.exe installer.py --install 1>stdout.txt 2>&1