'''get information about program's environment'''

from os import environ
from enum import Enum
from .utils import PATH

# Environment variables
HOME             =      environ.get('HOME')
XDG_CACHE_HOME   =      environ.get('XDG_CACHE_HOME',  f'{HOME}/.cache')
XDG_DATA_HOME    = PATH(environ.get('XDG_DATA_HOME',   f'{HOME}/.local/share'))
XDG_DATA_DIRS    = PATH(environ.get('XDG_DATA_DIRS',    '/usr/local/share:/usr/share'))
SYSTEM_DATA_DIRS = PATH(environ.get('SYSTEM_DATA_DIRS', '/usr/local/share:/usr/share'))

# Package Type and related stuff
from .enums import PackageType
PACKAGE_TYPE = PackageType.Unknown
HOST_ROOT    = ''

if environ.get('FLATPAK_ID'): # Flatpak
    PACKAGE_TYPE = PackageType.Flatpak
    HOST_ROOT    = '/var/run/host'
elif environ.get('APPDIR'):   # AppImage
    PACKAGE_TYPE = PackageType.AppImage
