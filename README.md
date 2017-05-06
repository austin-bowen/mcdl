# mcdl - Minecraft Downloader
A script for downloading pre-built Minecraft software, such as Spigot and CraftBukkit.

You can use mcdl to quickly download the latest .jar file for your favorite
Minecraft server, grab a specific server API version for plugin development,
etc. mcdl uses [Yive's Mirror](https://yivesmirror.com/) (no affiliation)
to download pre-built Minecraft software related to the following projects:
* [Bukkit / CraftBukkit](https://bukkit.org/)
* [BungeeCord](https://www.spigotmc.org/)
* Cauldron
* [Genisys](https://itxtech.org/genisys/)
* HexaCord
* MCPC
* [Nukkit](https://nukkit.io/)
* [PaperSpigot](https://github.com/PaperMC/Paper)
* [Spigot](https://www.spigotmc.org/)
* [TacoSpigot](https://github.com/TacoSpigot/TacoSpigot)
* [Thermos](https://cyberdynecc.github.io/Thermos/)
* [Waterfall](https://github.com/WaterfallMC/Waterfall)

## Usage
```
mcdl.py get <project> <file> [dest]  - Download the project file
mcdl.py list <project>               - List the project files
```

## Examples
#### Find and download a specific version of CraftBukkit
```
$ mcdl.py list craftbukkit
        Available CraftBukkit Files:
craftbukkit-0.0.1-SNAPSHOT.1000.jar
craftbukkit-0.0.1-SNAPSHOT.1060.jar
craftbukkit-1-6-6 beta.jar
craftbukkit-1.10-R0.1-SNAPSHOT-latest.jar
craftbukkit-1.10.2-R0.1-SNAPSHOT-latest.jar
...
$ mcdl.py get craftbukkit craftbukkit-1.10.2-R0.1-SNAPSHOT-latest.jar
Downloading CraftBukkit file "craftbukkit-1.10.2-R0.1-SNAPSHOT-latest.jar"...  Done.
Saving to file "./craftbukkit-1.10.2-R0.1-SNAPSHOT-latest.jar"...  Done.
$ ls
craftbukkit-1.10.2-R0.1-SNAPSHOT-latest.jar
```

#### Download a Spigot build to a specific path
```
$ mcdl.py get spigot spigot-latest.jar /path/to/server/spigot.jar
Downloading Spigot file "spigot-latest.jar"...  Done.
Saving to file "/path/to/server/spigot.jar"...  Done.
$ ls /path/to/server/
spigot.jar
```
Some time later (perhaps run by a cron job)...
```
$ mcdl.py get spigot spigot-latest.jar /path/to/server/spigot.jar
Downloading Spigot file "spigot-latest.jar"...  Done.
File "/path/to/server/spigot.jar" is already up-to-date
```

#### List MCPC files
```
$ mcdl.py list mcpc
        Available MCPC Files:
craftbukkitplusplus-1.2.5-R4.1-MCPC-SNAPSHOT.jar
mcpc-plus-1.4.7-R1.1-SNAPSHOT-f534-247.jar
mcpc-plus-1.4.7-R1.1-SNAPSHOT-f534-authfix1.jar
...
```

## Installation (Linux)
Note: mcdl.py was written for Linux and has not yet been tested on Windows or Mac.

If you want to be able to use the script from anywhere on your machine, then
you need to copy the mcdl.py file to a directory in your path.  The best place
to put it is most likely /usr/local/bin/.  The following steps show a typical
installation procedure:
```
$ sudo apt-get install python3-requests
$ cd /usr/local/src/
$ git clone https://github.com/SaltyHash/mcdl.git
$ cd mcdl
$ sudo cp mcdl.py /usr/local/bin/
```
You can now use mcdl.py from anywhere in your system.  To update mcdl.py:
```
$ cd /usr/local/src/mcdl/
$ git pull
$ sudo cp mcdl.py /usr/local/bin/
```
To remove mcdl.py and its repo from your system, run this:
```
$ sudo rm -i /usr/local/bin/mcdl.py
$ sudo rm -r /usr/local/bin/mcdl/
```

## Use Case: Setting up Automatic Updates (Linux)
You can use cron to automatically run mcdl.py to download the latest server file.
Here is a bare-bones example procedure for setting up cron to automatically
download the latest CraftBukkit .jar file every week:
1. `$ cd /etc/cron.weekly/`
1. `$ sudo touch upgrade-craftbukkit`
1. `$ sudo chmod +x upgrade-craftbukkit`
1. Edit the upgrade-craftbukkit file as super user with your favorite text
editor and write something like this:
```
#!/bin/sh

# Downloads the latest CraftBukkit .jar file

mcdl.py get craftbukkit craftbukkit-latest.jar /path/to/server/craftbukkit.jar

# Optionally some command here to restart your Minecraft server
# ...
```
cron will now run the upgrade-craftbukkit file every week, downloading the
latest CraftBukkit .jar file into your server's directory.

## To-do
* Download list of available projects rather than hard-coding them.
