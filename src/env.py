'''get information about program's environment'''

from os import environ
from enum import Enum
from .utils import PATH

# Environment variables
HOME             =      environ.get('HOME')
XDG_CACHE_HOME   =      environ.get('XDG_CACHE_HOME',  f'{HOME}/.cache')
XDG_DATA_HOME    =      environ.get('XDG_DATA_HOME',   f'{HOME}/.local/share')
XDG_DATA_DIRS    = PATH(environ.get('XDG_DATA_DIRS',    '/usr/local/share:/usr/share'))
SYSTEM_DATA_DIRS = PATH(environ.get('SYSTEM_DATA_DIRS', '/usr/local/share:/usr/share'))

# Package Type and related stuff
from .enums import PackageType
PACKAGE_TYPE = PackageType.Unknown
HOST_ROOT    = ''

if environ.get('FLATPAK_ID'): # Flatpak
    PACKAGE_TYPE = PackageType.Flatpak
    HOST_ROOT    = '/run/host'
elif environ.get('APPDIR'):   # AppImage
    PACKAGE_TYPE = PackageType.AppImage

# OS Release info
#from packaging.version import Version
from .utils import read_os_release
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
