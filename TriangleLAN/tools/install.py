import ctypes
import json
import os
import os.path
from os.path import join as j
import subprocess
import sys

root = os.path.abspath(j(os.path.dirname(sys.argv[0]), '..'))
desktop = os.path.expanduser(j('~', 'Desktop'))
archives_folder = j(root, 'archives')
games_folder = j(root, 'games')
unzipper = j(root, 'tools', '7za.exe')
shortcut = j(root, 'tools', 'Shortcut.exe')
uninstaller = j(root, 'tools', 'uninstall.bat')

def is_admin():
	# See https://stackoverflow.com/questions/1026431/cross-platform-way-to-check-admin-rights-in-a-python-script-under-windows
	return ctypes.windll.shell32.IsUserAnAdmin() != 0

def make_shortcut(target, dest, icon=None):
	if icon is None:
		icon = target
	
	wdir = os.path.dirname(target)

	# See http://www.optimumx.com/downloads.html#Shortcut for more info about shortcut.exe
	# Call shortcut.exe without any arguments to see help
	subprocess.run([shortcut, '/f:'+dest, '/a:c', '/t:'+target, '/i:'+icon, '/w:'+wdir])

# Creates a shortcut to an executable based on an executable definition
# An executable definition can be either:
#   A string, in which case the string is interpreted as a path to the executable, the shortcut name is the game name, and the shortcut icon is taken from the executable
#   A dictionary containing the executable path and optional overrides for the shortcut name and icon
def make_exe(game_name, exe_def):
	if isinstance(exe_def, str):
		make_shortcut(j(games_folder, exe_def), j(desktop, game_name+'.lnk'), None)
	else:
		# Check for shortcut name override
		name = game_name
		if 'name' in exe_def:
			name = exe_def['name']

		# Check for shortcut icon override
		icon = None
		if 'icon' in exe_def:
			icon = j(games_folder, exe_def['icon'])
		
		# Make shortcut
		make_shortcut(j(games_folder, exe_def['path']), j(desktop, name+'.lnk'), icon)

def unzip(archive, dest):
	subprocess.run([unzipper, 'x', archive, '-o'+dest, '-y'])

def install(game_name):
	print("Installing", game_name)

	# cd into the game folder
	src_folder = j(archives_folder, game_name)
	os.chdir(src_folder)
	# load config file
	config = json.load(open('config.json'))

	# check admin requirement
	if 'requires_admin' in config and not is_admin():
		print(game_name, "requires admin rights to install")
		return

	# run pre-install script
	if 'pre_script' in config:
		subprocess.run([config['pre_script'], src_folder])

	# install game
	if 'archive' in config:
		unzip(config['archive'], games_folder)
	if 'installer' in config:
		subprocess.run([config['installer']])

	# run post-install script
	if 'post_script' in config:
		subprocess.run([config['post_script'], src_folder])

	# create shortcut(s) to game executable(s)
	if 'exe' in config:
		make_exe(game_name, config['exe'])
	
	if 'exes' in config:
		for name, exe in config['exes'].items():
			make_exe(name, exe)


if __name__ == '__main__':
	install(sys.argv[1])