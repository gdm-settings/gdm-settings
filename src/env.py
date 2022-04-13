from os import environ
from enum import Enum
from .utils import PATH

PackageType = Enum('PackageType', ['NONE', 'AppImage', 'Flatpak'])
InterfaceType = Enum('InterfaceType', ['NONE', 'Graphical', 'CommandLine'])

HOME = environ.get('HOME')
XDG_CACHE_HOME = environ.get('XDG_CACHE_HOME', f"{HOME}/.cache")
SYSTEM_DATA_DIRS = PATH(environ.get('SYSTEM_DATA_DIRS', '/usr/local/share:/usr/share'))

INTERFACE_TYPE = InterfaceType.NONE

PACKAGE_TYPE = PackageType.NONE
HOST_ROOT = ''
if environ.get('FLATPAK_ID'): # Flatpak
    PACKAGE_TYPE = PackageType.Flatpak
    HOST_ROOT = '/var/run/host'
elif environ.get('APPDIR'):   # AppImage
    PACKAGE_TYPE = PackageType.AppImage
