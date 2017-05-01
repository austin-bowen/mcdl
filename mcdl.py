#!/usr/bin/env python3

'''mcdl.py - A script for downloading pre-built Minecraft software'''

__filename__ = 'mcdl.py'
__version__  = '0.1'
__depends__  = []
__author__   = 'Austin Bowen <austin.bowen.314@gmail.com>'

import requests
from datetime import datetime
from os.path import getmtime
from wsgiref.handlers import format_date_time

PROJECTS = [
    'Bukkit', 'BungeeCord', 'Cauldron', 'CraftBukkit', 'MCPC', 'PaperSpigot',
    'Spigot', 'TacoSpigot', 'Thermos',  'Waterfall',
]

def cmd_get(*args):
    try:
        project = args[0]
    except IndexError:
        print('ERROR: No project given')
        return 1
    
    try:
        project_file = args[1]
    except IndexError:
        print('ERROR: No project file given')
        return 1
    
    try:
        project_file = get_project_files(project)[project_file]
    except KeyError:
        print('ERROR: {} file "{}" does not exist'.format(
            get_project_title(project), project_file))
        return 2
    except ValueError:
        print('ERROR: Project "'+project+'" does not exist')
        return 2
    
    try:
        existing_file_modt = format_date_time(getmtime(project_file['name']))
    except FileNotFoundError:
        existing_file_modt = None
    
    print('Downloading {} file "{}"...'.format(
        get_project_title(project), project_file['name']))
    headers = {}
    if existing_file_modt:
        headers['If-Modified-Since'] = existing_file_modt
    req = requests.get(project_file['urls']['free'], headers=headers)
    try:
        if not req:
            print('ERROR: Download failed (HTTP status code '+\
                req.status_code+')')
            return 3
        if (req.status_code == requests.codes.not_modified):
            print('Existing file '+project_file['name']+' is already up-to-date')
            return 0
        project_file_data = req.content
    finally:
        req.close(); del req
    
    with open(project_file['name'], 'wb') as f:
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
    
    req = requests.get('https://yivesmirror.com/api/'+project)
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
        
        filename = sys.argv[0]
        print('Usage:')
        print('  {} get  <project> <file> - Download the project file'.format(
            filename))
        print('  {} list <project>        - List the project files'.format(
            filename))
        
        print('\nProjects:')
        for p in PROJECTS: print('  '+p)
        
        print('\nExample: Downloading the latest Spigot build')
        print('  $ {} get spigot spigot-latest.jar'.format(filename))
        
        print('\nDownloads supplied and hosted by '+\
            'Yive\'s Mirror (https://yivesmirror.com/)')
        
        sys.exit(0 if (cmd == None) else 1)
    
    cmd_func = globals()['cmd_'+cmd]
    result   = cmd_func(*sys.argv[2:])
    sys.exit(result or 0)
