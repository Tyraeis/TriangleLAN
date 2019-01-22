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
	
	dir = os.path.dirname(target)

	# See http://www.optimumx.com/downloads.html#Shortcut for more info about shortcut.exe
	subprocess.run([shortcut, '/f:'+dest, '/a:c', '/t:'+target, '/i:'+icon, '/w:'+dir])

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

	# check for icon override
	icon = None
	if 'icon' in config:
		icon = j(games_folder, config['icon'])

	# create shortcut to game executable
	make_shortcut(j(games_folder, config['exe']), j(desktop, game_name+'.lnk'), icon)


if __name__ == '__main__':
	install(sys.argv[1])