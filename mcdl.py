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
__version__  = '0.3.0'
__author__   = 'Austin Bowen <austin.bowen.314@gmail.com>'

import os
import requests
from hashlib import sha1
from packaging.version import parse as parse_version
from progress.bar import IncrementalBar
from six import print_
from terminaltables import AsciiTable
from time import time as wall_time

# Return codes
SUCCESS = 0
WARN_FILE_NOT_NEW     =  1
ERROR_INVALID_ARGS    = -1
ERROR_FILE_PERMS      = -2
ERROR_DOWNLOAD_FAILED = -3

HTTP_USER_AGENT = __filename__+'/'+__version__
PROJECTS = [
    'Bukkit',
    'BungeeCord',
    'Cauldron',
    'CraftBukkit',
    'Genisys',
    'Glowstone',
    'HexaCord',
    'HOSE',
    'MCPC',
    'Nukkit',
    'PaperSpigot',
    'Spigot',
    'TacoSpigot',
    'Thermos',
    'Torch',
    'Waterfall',
]

def cmd_get(*args):
    '''Handles command: get <project> <file> [dest]'''
    # Get the project name
    try:
        project = args[0]
    except IndexError:
        print_('ERROR: No project given\n')
        print_projects()
        return ERROR_INVALID_ARGS
    
    # Get the project file name
    try:
        project_file_name = args[1]
    except IndexError:
        print_('ERROR: No project file given')
        return ERROR_INVALID_ARGS
    
    # Get the project file destination
    try:
        file_dest = args[2]
    except IndexError:
        file_dest = os.curdir
    if os.path.isdir(file_dest):
        file_dest = os.path.join(file_dest, project_file_name)
    
    # Get project files
    project_files = get_project_files(project)
    # Project DNE?
    if (project_files == None):
        print_('ERROR: Project "'+project+'" does not exist\n')
        print_projects()
        return ERROR_INVALID_ARGS
    
    # Get project file
    project_file = get_project_file_named(project_file_name, project_files)
    # Project file DNE?
    if (project_file == None):
        print_('ERROR: {} file "{}" does not exist'.format(
            get_project_title(project), project_file_name))
        return ERROR_INVALID_ARGS
    
    # Download and save the project file and return the result
    return download_project_file(project_file, file_dest)

def cmd_list(*args):
    '''Handles command: list <project>'''
    # Get project
    try:
        project = args[0]
    except IndexError:
        print_('ERROR: No project given\n')
        print_projects()
        return ERROR_INVALID_ARGS
    
    # Get project files
    project_files = get_project_files(project)
    # Project DNE?
    if (project_files == None):
        print_('ERROR: Project "'+project+'" does not exist\n')
        print_projects()
        return ERROR_INVALID_ARGS
    
    # Sort project files by version ascending
    project_files = sorted(project_files,
        key=lambda pf: parse_version(pf['name']))
    
    # Build and print table of files
    rows = [[
        '{} Files'.format(get_project_title(project)),
        'MC Ver.',
        'Size',
    ]]
    for project_file in project_files:
        rows.append([
            project_file['name'],
            project_file['version']['minecraft'],
            project_file['size']['human'],
        ])
    table = AsciiTable(rows)
    table.outer_border = False
    table.padding_left = table.padding_right = 2
    print_(table.table)
    
    return SUCCESS

def download_project_file(project_file, file_dest):
    '''Downloads the project file content and saves it to the destination.
    If the destination is a directory and not a file name, then the project
    file content is saved to a file named using the project file name.
    If the project file is not newer than the file at the destination, then
    the project file content is not downloaded.
    
    Prints progress and errors.
    
    Returns: SUCCESS, ERROR_FILE_PERMS, or ERROR_DOWNLOAD_FAILED.
    '''
    # File destination is a directory?  Append the project file name.
    if os.path.isdir(file_dest):
        file_dest = os.path.join(file_dest, project_file['name'])
    
    # Do not have write permission for the file destination?
    if not os.access(os.path.dirname(os.path.abspath(file_dest)), os.W_OK):
        print_('ERROR: Do not have write permission for destination "{}"'.format(
            file_dest))
        return ERROR_FILE_PERMS
    
    # Return if the hashes match, implying no change
    try:
        # Get hash of local file
        with open(file_dest, 'rb') as f:
            file_hash = sha1(f.read()).hexdigest().casefold()
        
        # Hashes match?
        if (file_hash == project_file['hashes']['sha1'].casefold()):
            print_('File "'+file_dest+'" is already up-to-date')
            return WARN_FILE_NOT_NEW
        del file_hash
    except FileNotFoundError:
        pass
    
    # Set up HTTP request headers
    headers = {
        'User-Agent': HTTP_USER_AGENT,
    }
    
    # Start downloading the project file data
    print_('Downloading {} file "{}"...  '.format(
        project_file['project'], project_file['name']))
    req = requests.get(project_file['urls']['free'],
        headers=headers, stream=True)
    del headers
    
    # Failed to create request?
    if not req:
        print_('ERROR: Download failed (HTTP status code '+\
            req.status_code+')')
        return ERROR_DOWNLOAD_FAILED
    
    # Print the progress
    project_file_data = bytearray()
    bar = IncrementalBar(' ', max=project_file['size']['bytes'],
        suffix='%(percent)d%% of '+project_file['size']['human']+\
            ' (ETA %(eta_td)s)')
    t0 = 0
    for chunk in req.iter_content(chunk_size=8192):
        # Add new chunk to the project file data
        project_file_data.extend(chunk)
        
        # Update progress bar every 0.5 seconds or at end of download
        t1 = wall_time()
        if ((t1-t0) >= 0.5 or len(chunk) < 8192):
            bar.goto(len(project_file_data))
            t0 = t1
    bar.finish()
    req.close()
    del bar, req, t0, t1
    
    # Make sure the downloaded project file hash matches the expected hash
    actual_hash   = sha1(project_file_data).hexdigest().casefold()
    expected_hash = project_file['hashes']['sha1'].casefold()
    if (actual_hash != expected_hash):
        print_('WARNING: Downloaded file\'s SHA-1 hash value does not match'+\
            ' the expected hash value')
    del actual_hash, expected_hash
    
    # Save the project file to the destination
    print_('Saving to file "'+file_dest+'"...  ', end='', flush=True)
    with open(file_dest, 'wb') as f:
        f.write(project_file_data)
    print_('Done.')
    
    return SUCCESS

def get_project_file_named(name, project_files):
    '''Returns the project file for the given project, or None if either
    the project or project file does not exist.
    '''
    for project_file in project_files:
        if (project_file['name'] == name): return project_file
    return None

def get_project_files(project):
    '''Returns a list of files available for the given project,
    or None if the project does not exist.
    
    Example:
    >>> get_project_files('spigot')
    [
        {
            'name'   : 'spigot-latest.jar',
            'project': 'Spigot',
            'version': {
                'minecraft': '...'
            },
            'size': {
                'human': '23.40MB',
                'bytes': 24539208
            },
            'date': {
                'human': 'March 24, 2017',
                'epoch': 1493893504,
            },
            'urls': {
                'paid': 'http://...',
                'free': 'http://...'
            }
        },
        ...,
    ]
    '''
    # Get project title
    project_title = get_project_title(project)
    # Project DNE?
    if not project_title: return None
    
    # Download list of project files
    headers = {
        'User-Agent': HTTP_USER_AGENT,
    }
    req = requests.get('https://yivesmirror.com/api/'+project, headers=headers)
    req_json = req.json()
    req.close(); del req
    
    # Build and return list of project files
    project_files = []
    for entry in req_json:
        project_file = list(entry.values())[0]
        project_file['project'] = project_title
        project_files.append(project_file)
    return project_files

def get_project_title(project):
    '''Returns the project name's titled version, or None if project DNE.
    
    Example:
    >>> get_project_title('bungeecord')
    'BungeeCord'
    '''
    project = project.casefold()
    for title in PROJECTS:
        if (project == title.casefold()): return title
    return None

def print_projects():
    print_('Projects:')
    for p in PROJECTS: print_('  '+p)

def project_exists(project):
    '''Returns True if the given project is in PROJECTS (case insensitive).'''
    return project.casefold() in {p.casefold() for p in PROJECTS}

def main():
    import sys
    
    # Get command
    try:
        cmd = sys.argv[1].casefold()
    except IndexError:
        cmd = None
    
    # Command not given or not recognized?
    if cmd not in {'get', 'list'}:
        # Command not recognized?
        if (cmd != None): print_('ERROR: Unrecognized command "'+cmd+'"')
        
        # Print usage
        filename = os.path.basename(sys.argv[0])
        print_('Usage:')
        print_('  {} get  <project> <file> [dest]'.format(filename) +\
               '  Download the project file')
        print_('  {} list <project>              '.format(filename) +\
               '  List the project files')
        
        print_()
        print_projects()
        
        print_('\nExample: Downloading the latest Spigot build')
        print_('  $ {} get spigot spigot-latest.jar'.format(filename))
        
        print_('\nReturn Codes:')
        return_codes = (
            (SUCCESS,               'Success'),
            (WARN_FILE_NOT_NEW,     'Download unnecessary'),
            (ERROR_INVALID_ARGS,    'Invalid arguments'),
            (ERROR_FILE_PERMS,      'File access permission error'),
            (ERROR_DOWNLOAD_FAILED, 'Download failed'),
        )
        for return_code in return_codes:
            print_('{:4}: {}'.format(*return_code))
        del return_codes
        
        print_('\nDownloads hosted by '+\
            'Yive\'s Mirror (no affiliation): https://yivesmirror.com/')
        print_('View project source on GitHub: https://github.com/SaltyHash/mcdl')
        
        sys.exit(SUCCESS if (cmd == None) else ERROR_INVALID_ARGS)
    
    # Get the handler function for the command and execute it
    try:
        cmd_func = globals()['cmd_'+cmd.replace('-', '_')]
    except KeyError:
        raise RuntimeError(
            'Failed to find handler function for command "'+cmd+'"')
    result = cmd_func(*sys.argv[2:])
    sys.exit(result)

if (__name__ == '__main__'):
    main()
