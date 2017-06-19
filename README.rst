mcdl - Minecraft Downloader
===========================

A simple program for downloading pre-built Minecraft software, such as CraftBukkit and Spigot.

You can use mcdl to quickly download the latest .jar file for your
favorite Minecraft server, grab a specific server API version for plugin
development, etc. mcdl uses `Yive's Mirror <https://yivesmirror.com/>`_
(no affiliation) to download pre-built Minecraft software related to the
following projects:

* `Bukkit / CraftBukkit <https://bukkit.org/>`_
* `BungeeCord <https://www.spigotmc.org/>`_
* Cauldron
* `Genisys <https://itxtech.org/genisys/>`_
* `Glowstone <https://www.glowstone.net/>`_
* HexaCord
* `HOSE <https://github.com/softpak/HOSE>`_
* MCPC
* `Nukkit <https://nukkit.io/>`_
* `PaperSpigot <https://github.com/PaperMC/Paper>`_
* `Spigot <https://www.spigotmc.org/>`_
* `TacoSpigot <https://github.com/TacoSpigot/TacoSpigot>`_
* `Thermos <https://cyberdynecc.github.io/Thermos/>`_
* `Torch <https://github.com/TorchSpigot/Torch>`_
* `Waterfall <https://github.com/WaterfallMC/Waterfall>`_

Usage
-----

::

    mcdl get  <project> <file> [dest]  Download the project file
    mcdl list <project>                List the project files

Examples
--------

Find and download a specific version of CraftBukkit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    $ mcdl list craftbukkit
      CraftBukkit Files                     |  MC Ver      |  Size
    ----------------------------------------+--------------+------------
      craftbukkit-latest.jar                |  Latest      |  20.78MB
      craftbukkit-0.0.1-SNAPSHOT.1000.jar   |  1.7.3 Beta  |  8.11MB
      craftbukkit-0.0.1-SNAPSHOT.1060.jar   |  1.7.3 Beta  |  8.14MB
      ...
      craftbukkit-1.11-R0.1-SNAPSHOT.jar    |  1.11        |  19.05MB
      craftbukkit-1.11.2-R0.1-SNAPSHOT.jar  |  1.11.2      |  20.79MB
      craftbukkit.src.zip                   |  Unknown     |  880.63kB
    $ mcdl get craftbukkit craftbukkit-1.11.2-R0.1-SNAPSHOT.jar
    Downloading CraftBukkit file "craftbukkit-1.11.2-R0.1-SNAPSHOT.jar"...
      |████████████████████████████████| 100% of 20.79MB (ETA 0:00:00)
    Saving to file "./craftbukkit-1.11.2-R0.1-SNAPSHOT.jar"...  Done.
    $ ls
    craftbukkit-1.11.2-R0.1-SNAPSHOT.jar

Download a Spigot build to a specific path
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    $ mcdl get spigot spigot-latest.jar /path/to/server/spigot.jar
    Downloading Spigot file "spigot-latest.jar"...
      |████████████████████████████████| 100% of 23.40MB (ETA 0:00:00)
    Saving to file "/path/to/server/spigot.jar"...  Done.
    $ ls /path/to/server/
    spigot.jar

Some time later (perhaps run by a cron job)...

::

    $ mcdl get spigot spigot-latest.jar /path/to/server/spigot.jar
    File "/path/to/server/spigot.jar" is already up-to-date

Installation (Linux)
--------------------

If you have `Python3 <https://www.python.org/downloads/>`_ installed, then you
can use pip to install mcdl to your system:

::

    $ sudo pip3 install mcdl

To uninstall mcdl:

::

    $ sudo pip3 uninstall mcdl

To upgrade mcdl to the latest version:

::

    $ sudo pip3 install --upgrade mcdl

Use Case: Automatic Server Updates (Linux)
------------------------------------------

You can use cron to automatically run mcdl to download the latest
server file. Here is a bare-bones example procedure for setting up a cron job
to automatically download the latest CraftBukkit .jar file every week:

::

    $ cd /etc/cron.weekly/
    $ sudo touch upgrade-craftbukkit       # Create file
    $ sudo chmod +x upgrade-craftbukkit    # Make it executable

Now edit the upgrade-craftbukkit file as superuser with your favorite text editor and write something like this:

::

    #!/bin/sh
    
    # Downloads the latest CraftBukkit .jar file
    
    mcdl get craftbukkit craftbukkit-latest.jar /path/to/server/craftbukkit.jar
    
    # File downloaded?
    if [ $? -eq 0 ]; then
        # Optionally, some command here to restart your Minecraft server
        # ...
    fi

cron will now run the upgrade-craftbukkit file every week, downloading
the latest CraftBukkit .jar file into your server's directory.

To-do
-----

-  Download list of available projects rather than hard-coding them.
