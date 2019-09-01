@echo off
cd /d %~dp0
start "TriangleLAN Installer" python/pythonw.exe trianglelan.py --install 1>stdout.txt 2>&1

for /f %%i in (
	'powershell "(get-volume | where drivetype -eq removable).driveletter"'
) do "tools/RemoveDrive.exe" %%i: -L

powershell "$wshell=New-Object -ComObject Wscript.Shell;$wshell.Popup('USB Drive is save to remove',5,'TriangleLAN',0)"
exit