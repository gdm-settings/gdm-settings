from os import environ as env
from enum import Enum
from .utils import PATH

PackageType = Enum('PackageType', ['NONE', 'AppImage', 'Flatpak'])
InterfaceType = Enum('InterfaceType', ['NONE', 'Graphical', 'CommandLine'])

HOME = env.get('HOME')
XDG_CACHE_HOME = env.get('XDG_CACHE_HOME', f"{HOME}/.cache")
SYSTEM_DATA_DIRS = PATH(env.get('SYSTEM_DATA_DIRS', '/usr/local/share:/usr/share'))

INTERFACE_TYPE = InterfaceType.NONE

PACKAGE_TYPE = PackageType.NONE
HOST_ROOT = ''
if env.get('FLATPAK_ID'): # Flatpak
    PACKAGE_TYPE = PackageType.Flatpak
    HOST_ROOT = '/var/run/host'
elif env.get('APPDIR'):   # AppImage
    PACKAGE_TYPE = PackageType.AppImage
