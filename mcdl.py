# Copyright (c) 2017-2019 Austin Bowen
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

"""
mcdl.py - A script for downloading pre-built Minecraft software.

TODO: Use argparse.
TODO: Consider error cases.
"""

__filename__ = 'mcdl.py'
__version__ = '0.4.0'
__author__ = 'Austin Bowen <austin.bowen.314@gmail.com>'

import os
import shutil
import sys
from functools import lru_cache
from multiprocessing.pool import Pool
from tempfile import TemporaryDirectory
from typing import List

import requests
from packaging.version import parse as parse_version
from progress.bar import IncrementalBar
from six import print_
from terminaltables import AsciiTable

# Return codes
SUCCESS = 0
ERROR_GENERAL = 1
ERROR_INVALID_ARGS = -1
ERROR_FILE_PERMS = -2
ERROR_DOWNLOAD_FAILED = -3

API_ROOT = 'https://yivesmirror.com/api/'
HTTP_USER_AGENT = __filename__ + '/' + __version__
MAX_PARALLEL_REQUESTS = 10
REQUEST_HEADERS = {'User-Agent': HTTP_USER_AGENT}


class ProjectFile:
    def __init__(self, json: dict):
        self.size_human = json["size_human"]
        self.size_bytes = json["size_bytes"]
        self.file_name = json["file_name"]
        self.date_human = json["date_human"]
        self.date_epoch = json["date_epoch"]
        self.mc_version = json["mc_version"]
        self.direct_link = json["direct_link"]

    def __str__(self):
        return self.file_name


def _get_request(resource: str, **kwargs) -> requests.Response:
    return _get_request_raw(API_ROOT + resource, **kwargs)


def _get_request_raw(url: str, **kwargs) -> requests.Response:
    return requests.get(url, headers=REQUEST_HEADERS, **kwargs)


def cmd_get(*args) -> int:
    """Handles command: get <project> <file> [dest]"""

    # Get the project name
    try:
        project = args[0]
    except IndexError:
        print_('ERROR: No project given\n')
        print_projects()
        return ERROR_INVALID_ARGS

    # Get the project file name
    try:
        file_name = args[1]
    except IndexError:
        print_('ERROR: No project file given')
        return ERROR_INVALID_ARGS

    # Get the project file destination
    try:
        file_dest = args[2]
    except IndexError:
        file_dest = os.curdir
    if os.path.isdir(file_dest):
        file_dest = os.path.join(file_dest, file_name)

    # Get project file
    project_file = get_project_file(project, file_name)
    # Project file DNE?
    if project_file is None:
        print_('ERROR: {} file "{}" does not exist'.format(
            project, file_name))
        return ERROR_INVALID_ARGS

    # Download and save the project file and return the result
    return download_project_file(project, project_file, file_dest)


def cmd_list(*args):
    """Handles command: list <project>"""

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
    if project_files is None:
        print_(f'ERROR: Project {repr(project)} does not exist.\n')
        print_projects()
        return ERROR_INVALID_ARGS

    # Sort project files by version ascending
    project_files = sorted(project_files, key=lambda pf: parse_version(pf.file_name))

    # Build and print table of files
    rows = [(f'{project.title()} Files', 'MC Ver.', 'Size')]
    rows += [(pf.file_name, pf.mc_version, pf.size_human) for pf in project_files]
    table = AsciiTable(rows)
    table.outer_border = False
    table.padding_left = table.padding_right = 2
    print()
    print_(table.table)

    return SUCCESS


def download_project_file(project: str, project_file: ProjectFile, file_dest: str) -> int:
    """
    Downloads the project file content and saves it to the destination.
    If the destination is a directory and not a file name, then the project
    file content is saved to a file named using the project file name.
    If the project file is not newer than the file at the destination, then
    the project file content is not downloaded.

    Prints progress and errors.

    Returns: SUCCESS, ERROR_FILE_PERMS, or ERROR_DOWNLOAD_FAILED.
    """

    # File destination is a directory?  Append the project file name.
    if os.path.isdir(file_dest):
        file_dest = os.path.join(file_dest, project_file.file_name)

    # Do not have write permission for the file destination?
    if not os.access(os.path.dirname(os.path.abspath(file_dest)), os.W_OK):
        print_(f'ERROR: Do not have write permission for destination {repr(file_dest)}')
        return ERROR_FILE_PERMS

    # Start downloading the project file data
    print_(f'Downloading {project.title()} file {repr(project_file.file_name)}...')

    with TemporaryDirectory(prefix=__filename__ + '-') as tmp_dir:

        # Download the file to a tmp file
        with IncrementalBar(
                ' ',
                max=project_file.size_bytes,
                suffix=f'%(percent)d%% of {project_file.size_human} (ETA %(eta_td)s)'
        ) as bar, \
                open(os.path.join(tmp_dir, project_file.file_name), 'ab') as tmp_file, \
                _get_request_raw(project_file.direct_link, stream=True) as response:

            chunk_size = 2 ** 16
            bytes_written = 0
            for chunk in response.iter_content(chunk_size=chunk_size):
                bytes_written += tmp_file.write(chunk)
                bar.goto(bytes_written)

        # Make sure file was downloaded completely
        if bytes_written != project_file.size_bytes:
            print_(f'ERROR: Received {bytes_written} bytes, but expected {project_file.size_bytes}.')
            return ERROR_DOWNLOAD_FAILED

        # Move tmp file to destination
        print_(f'Saving to file {repr(file_dest)}...  ', end='', flush=True)
        shutil.move(tmp_file.name, file_dest)
        print('Done.')

    return SUCCESS


@lru_cache()
def get_project_file(project: str, file_name: str) -> ProjectFile:
    with _get_request(f'file/{project}/{file_name}') as req:
        return ProjectFile(req.json())


@lru_cache()
def get_project_file_names(project) -> List[str]:
    """
    Returns a list of files available for the given project.
    """

    # Project DNE?
    if not project_exists(project):
        raise ValueError(f'Project {repr(project)} does not exist.')

    # Download list of project files
    with _get_request(f'list/{project}') as req:
        return req.json()


@lru_cache()
def get_project_files(project: str) -> List[ProjectFile]:
    file_names = get_project_file_names(project)
    print(f'Getting info for {len(file_names)} {project} files...')

    with Pool(MAX_PARALLEL_REQUESTS) as pool:
        return pool.starmap(
            get_project_file,
            [(project, file_name) for file_name in file_names]
        )


@lru_cache()
def get_projects() -> List[str]:
    """Returns the list of available projects."""

    # Download list of projects
    with _get_request('list/all') as req:
        return sorted(req.json())


def print_projects() -> None:
    print_('Projects: {}'.format(', '.join(get_projects())))


@lru_cache()
def project_exists(project) -> bool:
    """Returns True if the given project is available."""
    return project.casefold() in {p.casefold() for p in get_projects()}


def main() -> None:
    # Get command
    try:
        cmd = sys.argv[1].casefold()
    except IndexError:
        cmd = None

    # Command not given or not recognized?
    if cmd not in {'get', 'list'}:
        # Command not recognized?
        if cmd is not None:
            print_('ERROR: Unrecognized command "' + cmd + '"')

        # Print usage
        filename = os.path.basename(sys.argv[0])
        print_('Usage:')
        print_('  {} get  <project> <file> [dest]'.format(filename) + '  Download the project file')
        print_('  {} list <project>              '.format(filename) + '  List the project files')

        print_()
        print_projects()

        print_('\nExample: Downloading a Spigot 1.12 snapshot')
        print_('  $ {} get spigot spigot-1.12-R0.1-SNAPSHOT-b1372.jar'.format(
            filename))

        print_('\nReturn Codes:')
        return_codes = (
            (SUCCESS, 'Success'),
            (ERROR_GENERAL, 'General error'),
            (ERROR_INVALID_ARGS, 'Invalid arguments'),
            (ERROR_FILE_PERMS, 'File access permission error'),
            (ERROR_DOWNLOAD_FAILED, 'Download failed'),
        )
        for return_code in return_codes:
            print_('{:4}: {}'.format(*return_code))
        del return_codes

        print_('\nDownloads hosted by ' + 'Yive\'s Mirror (no affiliation): https://yivesmirror.com/')
        print_('View project source on GitHub: https://github.com/SaltyHash/mcdl')

        sys.exit(SUCCESS if cmd is None else ERROR_INVALID_ARGS)

    # Get the handler function for the command and execute it
    try:
        cmd_func = globals()['cmd_' + cmd.replace('-', '_')]
    except KeyError:
        raise RuntimeError(
            'Failed to find handler function for command "' + cmd + '"')
    result = cmd_func(*sys.argv[2:])
    sys.exit(result)


if __name__ == '__main__':
    main()
