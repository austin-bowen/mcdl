# mcdl - Minecraft Downloader
A script for downloading pre-built Minecraft software, such as Spigot and CraftBukkit.

You can use mcdl to quickly download the latest .jar file for your favorite Minecraft server, grab a specific server API version for plugin development, etc. mcdl uses [Yive's Mirror](https://yivesmirror.com/) to download pre-built Minecraft software related to the following projects:
* [Bukkit / CraftBukkit](https://bukkit.org/)
* [BungeeCord](https://www.spigotmc.org/)
* Cauldron
* MCPC
* [PaperSpigot](https://github.com/PaperMC/Paper)
* [Spigot](https://www.spigotmc.org/)
* [TacoSpigot](https://github.com/TacoSpigot/TacoSpigot)
* [Thermos](https://cyberdynecc.github.io/Thermos/)
* [Waterfall](https://github.com/WaterfallMC/Waterfall)

## Usage
```
mcdl.py get  <project> <file> - Download the project file
mcdl.py list <project>        - List the project files
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
Downloading CraftBukkit file "craftbukkit-1.10.2-R0.1-SNAPSHOT-latest.jar"...
Done
$ ls
craftbukkit-1.10.2-R0.1-SNAPSHOT-latest.jar
```

#### Download the latest Spigot build
```
$ mcdl.py get spigot spigot-latest.jar
Downloading Spigot file "spigot-latest.jar"...
Done
$ ls
spigot-latest.jar
```
Some time later (perhaps run by a cron job)...
```
$ mcdl.py get spigot spigot-latest.jar
Downloading Spigot file "spigot-latest.jar"...
Existing file spigot-latest.jar is already up-to-date
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

## Installation
If you want to be able to use the script from anywhere on your machine, then you need to copy the mcdl.py file to a directory in your path.  The best place to put it is most likely /usr/local/bin/.  The following steps show a typical installation procedure:
```
$ git clone https://github.com/SaltyHash/mcdl.git
$ cd mcdl
$ sudo cp mcdl.py /usr/local/bin/
$ cd .. ; rm -r mcdl    # Don't need the repo anymore
```
You can now use mcdl.py from anywhere in your system.  To update mcdl.py, simply follow the installation instructions again.  To remove mcdl.py, run this:
```
$ sudo rm -i `which mcdl.py`
```

## Setting up Automatic Updates
You can use cron to automatically run mcdl.py to download the latest server file.  Here is a bare-bones example procedure for setting up cron to automatically download the latest Spigot .jar file every week:
1. `$ cd /etc/cron.weekly/`
1. `$ touch upgrade_spigot`
1. `$ chmod +x upgrade_spigot`
1. Edit the upgrade_spigot file with your favorite text editor and write something like:
```
#!/bin/sh

# Downloads the latest Spigot .jar file

cd /path/to/server/directory/
mcdl.py get spigot spigot-latest.jar
```
