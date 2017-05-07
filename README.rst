mcdl - Minecraft Downloader
===========================

A script for downloading pre-built Minecraft software, such as Spigot
and CraftBukkit.

You can use mcdl to quickly download the latest .jar file for your
favorite Minecraft server, grab a specific server API version for plugin
development, etc. mcdl uses `Yive's Mirror <https://yivesmirror.com/>`_
(no affiliation) to download pre-built Minecraft software related to the
following projects:

* `Bukkit / CraftBukkit <https://bukkit.org/>`_
* `BungeeCord <https://www.spigotmc.org/>`_
* Cauldron
* `Genisys <https://itxtech.org/genisys/>`_
* HexaCord
* MCPC
* `Nukkit <https://nukkit.io/>`_
* `PaperSpigot <https://github.com/PaperMC/Paper>`_
* `Spigot <https://www.spigotmc.org/>`_
* `TacoSpigot <https://github.com/TacoSpigot/TacoSpigot>`_
* `Thermos <https://cyberdynecc.github.io/Thermos/>`_
* `Waterfall <https://github.com/WaterfallMC/Waterfall>`_

Usage
-----

::

    mcdl.py get  <project> <file> [dest]  Download the project file
    mcdl.py list <project>                List the project files

Examples
--------

Find and download a specific version of CraftBukkit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    $ mcdl.py list craftbukkit
      CraftBukkit Files                              |  MC Ver      |  Size
    -------------------------------------------------+--------------+------------
      craftbukkit-latest.jar                         |  Latest      |  20.78MB
      craftbukkit-0.0.1-SNAPSHOT.1000.jar            |  1.7.3 Beta  |  8.11MB
      craftbukkit-0.0.1-SNAPSHOT.1060.jar            |  1.7.3 Beta  |  8.14MB
      ...
      craftbukkit-1.11-R0.1-SNAPSHOT.jar             |  1.11        |  19.05MB
      craftbukkit-1.11.2-R0.1-SNAPSHOT.jar           |  1.11.2      |  20.79MB
      craftbukkit.src.zip                            |  Unknown     |  880.63kB
    $ mcdl.py get craftbukkit craftbukkit-1.11.2-R0.1-SNAPSHOT.jar
    Downloading CraftBukkit file "craftbukkit-1.11.2-R0.1-SNAPSHOT.jar" (20.79MB)...  Done.
    Saving to file "./craftbukkit-1.11.2-R0.1-SNAPSHOT.jar"...  Done.
    $ ls
    craftbukkit-1.11.2-R0.1-SNAPSHOT.jar

Download a Spigot build to a specific path
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    $ mcdl.py get spigot spigot-latest.jar /path/to/server/spigot.jar
    Downloading Spigot file "spigot-latest.jar" (23.40MB)...  Done.
    Saving to file "/path/to/server/spigot.jar"...  Done.
    $ ls /path/to/server/
    spigot.jar

Some time later (perhaps run by a cron job)...

::

    $ mcdl.py get spigot spigot-latest.jar /path/to/server/spigot.jar
    Downloading Spigot file "spigot-latest.jar" (23.40MB)...  Done.
    File "/path/to/server/spigot.jar" is already up-to-date

Installation (Linux)
--------------------

Note: mcdl.py was written for Linux and has not yet been tested on
Windows or Mac.

If you want to be able to use the script from anywhere on your machine,
then you need to copy the mcdl.py file to a directory in your path. The
best place to put it is most likely /usr/local/bin/. The following steps
show a typical installation procedure:

::

    $ cd /usr/local/src/
    $ sudo git clone https://github.com/SaltyHash/mcdl.git
    $ cd mcdl
    $ sudo pip3 install -r requirements.txt
    $ sudo cp mcdl.py /usr/local/bin/

You can now use mcdl.py from anywhere in your system. To update mcdl.py:

::

    $ cd /usr/local/src/mcdl/
    $ sudo git pull
    $ sudo cp mcdl.py /usr/local/bin/

To remove mcdl.py and its repo from your system, respectively, run this:

::

    $ sudo rm -i /usr/local/bin/mcdl.py
    $ sudo rm -r /usr/local/src/mcdl/

Use Case: Setting up Automatic Updates (Linux)
----------------------------------------------

You can use cron to automatically run mcdl.py to download the latest
server file. Here is a bare-bones example procedure for setting up cron
to automatically download the latest CraftBukkit .jar file every week:

#. ``$ cd /etc/cron.weekly/``
#. ``$ sudo touch upgrade-craftbukkit``
#. ``$ sudo chmod +x upgrade-craftbukkit``
#. Edit the upgrade-craftbukkit file as super user with your favorite text editor and write something like this:

::

    #!/bin/sh
    
    # Downloads the latest CraftBukkit .jar file
    
    mcdl.py get craftbukkit craftbukkit-latest.jar /path/to/server/craftbukkit.jar
    
    # Optionally some command here to restart your Minecraft server
    # ...

cron will now run the upgrade-craftbukkit file every week, downloading
the latest CraftBukkit .jar file into your server's directory.

To-do
-----

-  Download list of available projects rather than hard-coding them.
