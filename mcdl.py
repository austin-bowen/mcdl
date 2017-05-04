#!/usr/bin/env python3

# Copyright (c) 2017 Austin Bowen
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

'''mcdl.py - A script for downloading pre-built Minecraft software'''

__filename__ = 'mcdl.py'
__version__  = '0.1'
__depends__  = []
__author__   = 'Austin Bowen <austin.bowen.314@gmail.com>'

import os
import requests
from datetime import datetime
from wsgiref.handlers import format_date_time

PROJECTS = [
    'Bukkit', 'BungeeCord', 'Cauldron', 'CraftBukkit', 'MCPC', 'PaperSpigot',
    'Spigot', 'TacoSpigot', 'Thermos',  'Waterfall',
]
HTTP_USER_AGENT = __filename__+'/'+__version__

def cmd_get(*args):
    # Get the project name
    try:
        project = args[0]
    except IndexError:
        print('ERROR: No project given')
        return 1
    
    # Get the project file name
    try:
        project_file_name = args[1]
    except IndexError:
        print('ERROR: No project file given')
        return 1
    
    # Get the project file destination
    try:
        file_dest = args[2]
    except IndexError:
        file_dest = project_file_name
    file_dest = os.path.abspath(file_dest)
    if os.path.isdir(file_dest):
        file_dest = os.path.join(file_dest, project_file_name)
    
    # Make sure we have write permission for the file destination
    if not os.access(os.path.dirname(file_dest), os.W_OK):
        print('ERROR: Do not have write permission for destination "{}"'.format(
            file_dest))
        return 2
    
    # Get the project file info
    try:
        project_file = get_project_files(project)[project_file_name]
    except KeyError:
        print('ERROR: {} file "{}" does not exist'.format(
            get_project_title(project), project_file_name))
        return 3
    except ValueError:
        print('ERROR: Project "'+project+'" does not exist')
        return 3
    
    # Get file destination modification time
    try:
        existing_file_modt = format_date_time(os.path.getmtime(file_dest))
    except FileNotFoundError:
        existing_file_modt = None
    
    # Download the project file data
    print('Downloading {} file "{}" ...'.format(
        get_project_title(project), project_file_name))
    ## Set up HTTP request headers
    headers = {
        'User-Agent': HTTP_USER_AGENT,
    }
    if existing_file_modt:
        headers['If-Modified-Since'] = existing_file_modt
    req = requests.get(project_file['urls']['free'], headers=headers)
    try:
        if not req:
            print('ERROR: Download failed (HTTP status code '+\
                req.status_code+')')
            return 4
        if (req.status_code == requests.codes.not_modified):
            print('File "'+file_dest+'" is already up-to-date')
            return 0
        project_file_data = req.content
    finally:
        if req: req.close()
        del req
    
    # Save the project file to the destination
    print('Saving to file "'+file_dest+'" ...')
    with open(file_dest, 'wb') as f:
        f.write(project_file_data)
    print('Done')
    return 0

def cmd_list(*args):
    try:
        project = args[0]
    except IndexError:
        print('ERROR: No project given')
        return 1
    
    try:
        project_files = get_project_files(project)
    except ValueError:
        print('ERROR: Project "'+project+'" does not exist')
        return 1
    
    project_files = get_project_files(project)
    project_files = list(project_files.keys())
    project_files.sort()
    print('\tAvailable {} Files:'.format(get_project_title(project)))
    for pf in project_files: print(pf)
    return 0

def get_project_files(project):
    '''Returns a dict of the files available for the given project.
    
    Example:
    >>> get_project_files('spigot')
    {
        'spigot-latest.jar': {...},
        'spigot-1.4.7-R1.1-SNAPSHOT.jar': {...},
        ...,
    }
    '''
    project  = project.lower()
    projects = {p.lower() for p in PROJECTS}
    if project not in projects:
        raise ValueError('Project "'+project+'" does not exist')
    
    headers = {
        'User-Agent': HTTP_USER_AGENT,
    }
    req = requests.get('https://yivesmirror.com/api/'+project, headers=headers)
    req_json = req.json()
    req.close(); del req
    
    project_files = {}
    for entry in req_json:
        filename = list(entry.keys())[0]
        project_files[filename] = entry[filename]
    return project_files

def get_project_title(project):
    '''Simply returns the project name's titled version.
    
    Example:
    >>> get_project_title('bungeecord')
    'BungeeCord'
    '''
    project = project.lower()
    for title in PROJECTS:
        if (project == title.lower()): return title
    return project.title()

if (__name__ == '__main__'):
    import sys
    
    cmd = None
    try:
        cmd = sys.argv[1].lower()
    except IndexError:
        pass
    
    if cmd not in {'get', 'list'}:
        if (cmd != None):
            print('ERROR: Unrecognized command "'+cmd+'"')
        
        filename = sys.argv[0].rpartition(os.path.sep)[2]
        print('Usage:')
        print('  {} get  <project> <file> [dest]  - Download the project file'.format(
            filename))
        print('  {} list <project>                - List the project files'.format(
            filename))
        
        print('\nProjects:')
        for p in PROJECTS: print('  '+p)
        
        print('\nExample: Downloading the latest Spigot build')
        print('  $ {} get spigot spigot-latest.jar'.format(filename))
        
        print('\nDownloads supplied and hosted by '+\
            'Yive\'s Mirror (https://yivesmirror.com/)')
        print('View the source on GitHub (https://github.com/SaltyHash/mcdl)')
        
        sys.exit(0 if (cmd == None) else 1)
    
    cmd_func = globals()['cmd_'+cmd]
    result   = cmd_func(*sys.argv[2:])
    sys.exit(result or 0)
