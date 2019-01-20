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

import libtorrent as lt
from tkinter import *
from tkinter import font
from tkinter.ttk import *

root = os.path.abspath(os.path.dirname(sys.argv[0]))
desktop = os.path.expanduser(j('~', 'Desktop'))
archives_folder = j(root, 'archives')
python = j(root, 'python', 'python.exe')
installer = j(root, 'tools', 'install.py')
uninstaller = j(root, 'tools', 'uninstall.bat')

def is_admin():
	# See https://stackoverflow.com/questions/1026431/cross-platform-way-to-check-admin-rights-in-a-python-script-under-windows
	return ctypes.windll.shell32.IsUserAnAdmin() != 0

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
			os.remove(j(desktop, item.name+'.lnk'))
	# Use uninstaller bat file to delete the TriangleLAN folder
	shutil.copyfile(uninstaller, j(root, 'uninstall.bat'))
	subprocess.Popen([j(root, 'uninstall.bat')])
	sys.exit() # The uninstaller will forcibly kill this program, but might as well try to exit gracefully first


#############
#  Torrent  #
#############

def make_session():
	ses = lt.session({
		'enable_incoming_utp': False,
		'enable_outgoing_utp': False,
		'enable_dht': False,
		'broadcast_lsd': True
	})
	ses.listen_on(19684, 19694)
	ses.start_lsd() # local service discovery
	return ses

def start_torrent(ses, file, save_path):
	e = lt.bdecode(open(file, 'rb').read())
	info = lt.torrent_info(e)
	params = { 'save_path': save_path, 'storage_mode': lt.storage_mode_t.storage_mode_sparse, 'ti': info }
	return ses.add_torrent(params)

#################
#  Coordinator  #
#################

coord_port = 19683

# The coordinator allows miscellaneous messages to be sent between computers running the installer.
# Right now it's just used to make it easy to uninstall the games from many computers at once
def run_coordinator():
	with socket(AF_INET, SOCK_DGRAM) as s:
		s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
		s.bind(('', coord_port))

		# Main loop
		while True:
			# Receive & parse packet
			(data, addr) = s.recvfrom(4096)
			msg = str(data, 'utf-8').split(':')
			print(msg)

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
		s.sendto(bytes('TriangleLAN:'+':'.join(msg), 'utf-8'), ('<broadcast>', coord_port))

#########
#  GUI  #
#########

si_prefixes = [' ', 'K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']
status_format = 'up: {:6.2f} {}b/s   down: {:6.2f} {}b/s   peers: {:2d}   eta: {:2d}:{:02d}'

def _format_speed(total):
	if total <= 0:
		return (0, ' ')

	unit = math.log(total) // math.log(1024)
	return (total / 1024**unit, si_prefixes[unit])

def _format_time(remaining, rate):
	if remaining <= 0 or rate <= 0:
		return (0, 0)

	secs = remaining / rate
	return '{:2d}:{:2d}'.format(secs % 60, secs // 60)


# This class controls the torrent info GUI
class GUI:
	def __init__(self):
		self.root = Tk()
		self.root.title("TriangleLAN")

		fnt = font.Font(family='Courier', size=12)
		style = Style()
		style.configure("TLabel", font=fnt)

		main = Frame(self.root, padding='6 6 6 6')
		main.grid(row=0, column=0, sticky=(N, E, S, W))
		main.rowconfigure(0, weight=1)
		main.columnconfigure(0, weight=1)

		self.top_status = StringVar(value="checking")
		self.percent = StringVar(value="  0.0%")
		self.bot_status = StringVar(value=status_format.format(0, 'M', 0, 'M', 0, 0, 0))

		Label(main, textvariable=self.top_status).grid(row=0, column=0, columnspan=2, sticky=W)
		Label(main, textvariable=self.percent).grid(row=1, column=0, sticky=W)
		self.progress = Progressbar(main, orient=HORIZONTAL, length=550, mode='determinate', maximum=1000000)
		self.progress.grid(column=1, row=1)
		Label(main, textvariable=self.bot_status).grid(row=2, column=0, columnspan=2, sticky=W)

		for child in main.winfo_children(): child.grid_configure(padx=5, pady=5)

	def mainloop(self):
		self.root.mainloop()

	def update(self, status):
		(down_speed, down_unit) = _format_speed(status.download_rate)
		(up_speed, up_unit) = _format_speed(status.upload_rate)
		peers = status.num_peers
		(min_left, sec_left) = _format_time(status.total_wanted, status.download_rate)

		self.top_status.set(status.state)
		self.percent.set('{:5.1f}%'.format(status.progress * 100))
		self.bot_status.set(status_format.format(down_speed, down_unit, up_speed, up_unit, peers, min_left, sec_left))
		self.progress['value'] = status.progress_ppm

	def update_loop(self, torrent):
		installed = False

		while True:
			s = torrent.status()
			self.update(s)
			if s.is_seeding and not installed:
				installed = True
				install_all()

			# Print alerts
			for alert in session.pop_alerts():
				print(alert.what() + ': ' + alert.message())

			time.sleep(0.1)

##########
#  Main  #
##########

noadmin_cache = {}
def filter_noadmin(path):
	path = os.path.relpath(path, archives_folder)
	game_name = path.split('\\')[0]

	if game_name in noadmin_cache:
		return noadmin_cache[game_name]
	
	# load game config and check whether it requests admin rights
	try:
		config = json.load(open(j(archives_folder, game_name, 'config.json')))
		a = not 'requires_admin' in config
	except FileNotFoundError:
		a = True # default to including items, just in case

	noadmin_cache[game_name] = a
	return a

def make_torrent(out, flt=lambda x: True):
	os.chdir(root)

	print('Collecting files...')
	fs = lt.file_storage()
	lt.add_files(fs, 'archives', flt)
	
	print('Generating piece hashes...')
	t = lt.create_torrent(fs)
	lt.set_piece_hashes(t, '.')

	print('Writing torrent file...')
	with open(out, 'wb') as f:
		f.write(lt.bencode(t.generate()))

	print('Torrent created')


if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(description='TriangleLAN Installer')
	parser.add_argument('--install', '-i', help='run the installer', action='store_true')
	parser.add_argument('--uninstall', '-u', help='remove TriangleLAN from this computer', action='store_true')
	parser.add_argument('--broadcast_uninstall', '-b', help='broadcast the uninstall packet, removing TriangleLAN from all computers', action='store_true')
	parser.add_argument('--make_torrents', '-t', help='recreate the archives torrent file', action='store_true')

	args = parser.parse_args()

	if args.broadcast_uninstall:
		broadcast('uninstall')

	if args.uninstall:
		uninstall()
		# we can't do anything else after uninstalling, ignore the rest of the options
		sys.exit()

	if args.make_torrents:
		make_torrent('archives_admin.torrent')
		make_torrent('archives_noadmin.torrent', flt=filter_noadmin)

	if args.install:
		torrent_file = 'archives_noadmin.torrent'
		if is_admin():
			torrent_file = 'archives_admin.torrent'

		session = make_session()
		torrent = start_torrent(session, torrent_file, root)
		gui = GUI()

		Thread(target=run_coordinator).start()
		Thread(target=gui.update_loop, args=[torrent], daemon=True).start()
		
		gui.mainloop()