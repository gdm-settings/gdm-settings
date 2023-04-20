'''get information about program's environment'''

import os
import re
import ast
import sys
import subprocess

from gi.repository import GLib

from gdm_settings import APP_ID
from .enums import PackageType


def read_os_release():
    filename = None
    for fn in '/run/host/os-release', '/etc/os-release', '/usr/lib/os-release':
        if os.path.isfile(fn):
            filename = fn
            break

    if filename is None:
        return

    os_release = []
    with open(filename, 'r') as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()         # Strip whitespace

            if not line or line.startswith('#'):
                continue

            if m := re.match(r'([A-Z][A-Z_0-9]+)=(.*)', line):
                name, val = m.groups()
                if val and val[0] in '"\'':
                    val = ast.literal_eval(val)
                os_release.append((name, val))
            else:
                print(f'{filename}:{line_number}: bad line {line!r}',
                      file=sys.stderr)

    return dict(os_release)

class PATH (list):
    '''
    A list to store values of PATH-like environment variables

    For example, with
        mypath = PATH('/usr/local/bin:/usr/bin')
    OR
        mypath = PATH(['/usr/local/bin', '/usr/bin'])
    we get,
        print(mypath)       # prints /usr/local/bin:/usr/bin
        print(*mypath)      # prints /usr/local/bin /usr/bin
        print(mypath[0])    # prints /usr/local/bin
        print(repr(mypath)) # prints PATH(['/usr/local/bin', '/usr/bin'])
    '''

    def __init__ (self, value=None, /):
        if value is None:
            return list.__init__(self)
        elif isinstance(value, str):
            value = value.strip(':').split(':')
        return list.__init__(self, value)

    def __str__ (self, /):
        return ':'.join(self)

    def __repr__ (self, /):
        return self.__class__.__name__ + '(' + list.__repr__(self) + ')'

    def copy (self, /):
        return self.__class__(self)


# XDG Base Directories
XDG_CONFIG_HOME = GLib.get_user_config_dir()
XDG_RUNTIME_DIR = GLib.get_user_runtime_dir()


# Application-specific Directories
TEMP_DIR       = os.path.join(XDG_RUNTIME_DIR, 'app', APP_ID)
HOST_DATA_DIRS = PATH(os.environ.get('HOST_DATA_DIRS', '/usr/local/share:/usr/share'))


# Package Type and related stuff
PACKAGE_TYPE = PackageType.Unknown
HOST_ROOT    = ''

if os.environ.get('FLATPAK_ID'): # Flatpak
    PACKAGE_TYPE = PackageType.Flatpak
    HOST_ROOT    = '/run/host'
elif os.environ.get('APPDIR'):   # AppImage
    PACKAGE_TYPE = PackageType.AppImage


# OS Release info
os_release = read_os_release()

OS_NAME       = os_release.get('NAME',       'Linux')
OS_ID         = os_release.get('ID',         'linux')
OS_ID_LIKE    = os_release.get('ID_LIKE',    'linux')
OS_VERSION_ID = os_release.get('VERSION_ID', '0')
OS_VERSION    = os_release.get('VERSION', OS_VERSION_ID)

OS_VERSION_CODENAME = os_release.get('VERSION_CODENAME')
_pretty_name = f'{OS_NAME} {OS_VERSION}'
if OS_VERSION_CODENAME: _pretty_name += f' ({OS_VERSION_CODENAME})'

OS_PRETTY_NAME = os_release.get('PRETTY_NAME', _pretty_name)

OS_IDs = [OS_ID] + OS_ID_LIKE.split()


def run_on_host(command, *args, **kwargs):
    if isinstance(command, str):
        command = [command]

    if PACKAGE_TYPE is PackageType.Flatpak:
        command = ['flatpak-spawn', '--host'] + command

    return subprocess.run(command, *args, **kwargs)