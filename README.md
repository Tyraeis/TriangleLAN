# TriangleLAN
TriangleLAN is a set of scripts used to install all the games we provide for LAN parties. It is primarily written in Python, and is thoroughly commented so it should be fairly easy to understand.

## Usage
To prepare for a LAN party, the TriangleLAN files should be copied onto several USB flash drives in advance.

Installing:

1. Log into the computer
2. Insert one of the USB drives
3. Run the `install.bat` script (the one outside the TriangleLAN folder)
4. Wait for the script to finish copying the files to the computer. You'll know it's done when several terminal windows open up
5. Eject the USB from the computer, or wait for the script to eject it automatically. One of the terminal windows will show a green success message if the USB was automatically ejected
6. Repeat this process for the rest of the computers

Uninstalling:

1. On one of the computers with TriangleLAN installed, open the TriangleLAN folder on the desktop
2. Run the `broadcast-uninstall.bat` script to remove TriangeLAN from all computers on the local network
3. If that doesn't work properly, you can also run the `uninstall.bat` script to just uninstall it locally
4. Log out of all of the computers

The rest of this document explains how the TriangleLAN script works and how to add new games.

## Directory Structure
```
TriangleLAN               #
 |  archives              # All games in this folder will be installed
 |   |  mygame            # Example game
 |   |   |  mygame.7z     # Zipped game files for mygame
 |   |   |  config.json   # Configuration for mygame
 |   |  <other games>     #
 |  games                 # Game files are unzipped into this folder
 |  python                # Portable python installation — used to run
 |   |  python.exe        #   the install scripts
 |   |  <other python files>
 |  tools                 # Tools used by the installer
 |   |  7za.exe           # Used to unzip game files
 |   |  RemoveDrive.exe   # Used to automatically eject USB drives
 |   |  Shortcut.exe      # Used to make desktop shortcuts
 |   |  install.py        # Used internally for installation
 |   |  uninstall.bat     # Used internally for uninstallation
 |  install.bat           # Used internally for installation
 |  trianglelan.py        # Main installer code 
 |  uninstall.bat         # Run to uninstall local files
 |  broadcast-uninstall.bat # Run to uninstall files from all computers on the local network
install.bat               # Run from USB to install
```

## How it Works
1. The outer `install.bat` copies the entire TriangleLAN folder onto the target computer's desktop, then runs the inner `install.bat` script inside the TriangleLAN folder on the target computer.
2. The inner `install.bat` ejects the USB drive and starts the python script.
3. The python script scans the archives folder, and starts a new process to run `tools/install.py` for each game archive it finds.
4. This script reads the game's `config.json`, then:
  1. runs pre_script, if specified (rare)
  2. unzips the specified archive file into the games folder
  3. runs an installer, if specified (rare)
  4. runs post_script, if specified (rare)
  5. creates desktop shortcuts to the game's executables
5. The python script also starts a UDP server which listens for a message to uninstall. This is used by the `broadcast-uninstall.bat` script.
6. When `uninstall.bat` is run, either manually or after receiving an uninstall message:
  1. All desktop shortcuts created by the installer are removed
  2. Any uninstall scripts specified an any game's `config.json` are run
  3. The TriangleLAN folder is deleted from the desktop

## Adding a New Game
A game is defined by a folder inside the archives folder. This folder should have the same name as the game, and should contain a `config.json` file which defines how to install/uninstall the game.

config.json Schema
```
{
    "archive": string,
    "installer": string,
    "exe": string|ExeDef,
    "exes": { string: string|ExeDef },
    "requires_admin": bool,
    "pre_script": string,
    "post_script": string,
    "uninstall_script": string
}
```

All of these settings are optional, and will do nothing if not specified. A basic game will just use the archive and exe settings, though the others are available if needed.

### archive
Path to the zipped game files, relative to the game folder (the folder `config.json` is in). If specified, this archive will be unzipped into the games folder on the target computer. The archive should be a 7z archive, which can be created with 7zip.

### installer
If specified, this script will be run to install the game. This will run after the archive is unzipped, if both are specified. The script should be placed in the game folder.

### exe
Defines the main executable for this game. If specified, a shortcut will be created to this executable. If this is a string, then the string should be the path to the executable within the archive, and the name of the shortcut will be the name of the game folder. For more control this can instead be an ExeDef object, which is defined further below.

### exes
A dictionary defining multiple executables to create shortcuts for. If this is specified, a shortcut will be created for each entry in this dictionary. The entry key will be the default name of the shortcut, and the entry value will be the definition of the executable to link to, defined in the same way as the `exe` option.

### requires_admin
If this is set to true, the installer will refuse to install the game if the installer isn't run with admin privileges.

### pre_script
If specified, this script will be run before the game archive is unzipped and/or the installer is run. The script should be placed in the game folder.

### post_script
If specified, this script will be run after the game archive is unzipped and/or the installer is run. The script should be placed in the game folder.

### uninstall_script
If specified, this script will be run before the game is uninstalled. It will run after the shortcuts have been cleaned up, before the game files are deleted. The script should be placed in the game folder.

### ExeDef Schema
```
{
    "name": string,
    "path": string,
    "icon": string
}
```

#### name
If specified, this name is used for the shortcut instead of the default.

#### path
The path to the executable to link to within the archive.

#### icon
If specified, the icon at this location will be used for the shortcut instead of the icon of the executable.


Example config.json

Consider this game folder:

```
archives
 |  mygame
 |   |  config.json
 |   |  mygame.7z
 |   |   |  mygame
 |   |   |   |  mygame.exe
 |   |   |   |  mygame-server.bat
 |   |   |   |  mygame-editor.exe
 |   |  my_pre_script.bat
 |   |  my_post_script.bat
 |   |  uninstall.bat
 ```

A config.json for "mygame" might look like this:

```
{
    "archive": "mygame.7z",
    "exe": "mygame/mygame.exe",
    "exes": {
        "mygame editor": "mygame/mygame-editor.exe",
        "mygame server": {
            "path": "mygame/mygame-server.bat",
            "icon": "mygame/mygame.exe"
        }
    },
    "pre_script": "my_pre_script.bat",
    "post_script": "my_post_script.bat",
    "uninstall_script": "uninstall.bat"
}
```

This will run `my_pre_script.bat`, unzip mygame.7z into the games folder, create "mygame", "mygame editor", and "mygame server" desktop shortcuts, and finally run `my_post_script.bat`. The "mygame server" shortcut will use the same icon as the base game, since the bat file it links to doesn't have a useful icon. When the game is being uninstalled, `uninstall.bat` will be run.
