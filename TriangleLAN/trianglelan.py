import ctypes
import json
import math
import os
import os.path
from os.path import join as j
import shutil
import subprocess
import sys
from socket import *
from threading import Thread
import time

root = os.path.abspath(os.path.dirname(sys.argv[0]))
desktop = os.path.expanduser(j('~', 'Desktop'))
archives_folder = j(root, 'archives')
python = j(root, 'python', 'python.exe')
installer = j(root, 'tools', 'install.py')
uninstaller = j(root, 'tools', 'uninstall.bat')

###############
#  Installer  #
###############

def install(game_name):
	# Having a seperate installer script allows all of the games to be installed in parallel and gives each installer its own console window
	subprocess.Popen([python, installer, game_name], creationflags=subprocess.CREATE_NEW_CONSOLE)

def install_all():
	for item in os.scandir(archives_folder):
		if item.is_dir():
			install(item.name)

def uninstall():
	# This should remove all traces of each game and the installer itself
	# Delete all created shortcuts
	for item in os.scandir(archives_folder):
		if item.is_dir():
			try:
				os.remove(j(desktop, item.name+'.lnk'))
			except FileNotFoundError:
				pass # os.remove can error if the file does not exist, which is obviously not a problem
	# Use uninstaller bat file to delete the TriangleLAN folder
	shutil.copyfile(uninstaller, j(root, 'uninstall.bat'))
	subprocess.Popen([j(root, 'uninstall.bat')])
	sys.exit() # The uninstaller will forcibly kill this program, but might as well try to exit gracefully first

##############
#  Listener  #
##############

port = 19683

# The listener allows messages to be sent between computers running the installer.
# Right now it's just used to make it easy to uninstall the games from many computers at once
def run_listener():
	with socket(AF_INET, SOCK_DGRAM) as s:
		s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
		s.bind(('', port))

		# Main loop
		while True:
			# Receive & parse packet
			(data, addr) = s.recvfrom(4096)
			msg = str(data, 'utf-8').split(':')

			# Ignore non-trianglelan packets
			if msg[0] != 'TriangleLAN':
				continue

			print(" <-", str(data, 'utf-8'))

			if msg[1] == 'uninstall':
				print('Uninstalling...')
				uninstall()

def broadcast(*msg):
	with socket(AF_INET, SOCK_DGRAM) as s:
		s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
		s.sendto(bytes('TriangleLAN:'+':'.join(msg), 'utf-8'), ('<broadcast>', port))

##########
#  Main  #
##########

if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(description='TriangleLAN Installer')
	parser.add_argument('--install', '-i', help='run the installer', action='store_true')
	parser.add_argument('--uninstall', '-u', help='remove TriangleLAN from this computer', action='store_true')
	parser.add_argument('--broadcast_uninstall', '-b', help='broadcast the uninstall packet, removing TriangleLAN from all computers', action='store_true')

	args = parser.parse_args()

	if args.install:
		Thread(target=install_all).start()
		run_listener()

	elif args.uninstall:
		uninstall()

	elif args.broadcast_uninstall:
		broadcast('uninstall')