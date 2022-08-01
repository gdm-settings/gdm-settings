'''get information about program's environment'''

import os
from .utils import PATH

# Environment variables
HOME           =      os.environ.get('HOME')
XDG_CACHE_HOME =      os.environ.get('XDG_CACHE_HOME',  f'{HOME}/.cache')
XDG_DATA_DIRS  = PATH(os.environ.get('XDG_DATA_DIRS',    '/usr/local/share:/usr/share'))
HOST_DATA_DIRS = PATH(os.environ.get('HOST_DATA_DIRS', '/usr/local/share:/usr/share'))

# Package Type and related stuff
from .enums import PackageType
from .info import project_name
PACKAGE_TYPE = PackageType.Unknown
TEMP_DIR     = os.path.join(XDG_CACHE_HOME, project_name) # ~/.cache/gdm-settings
HOST_ROOT    = ''

if os.environ.get('FLATPAK_ID'): # Flatpak
    PACKAGE_TYPE = PackageType.Flatpak
    TEMP_DIR     = os.path.join(XDG_CACHE_HOME, 'tmp') # ~/.var/app/io.github.realmazharhussain.GdmSettings/cache/tmp
    HOST_ROOT    = '/run/host'
elif os.environ.get('APPDIR'):   # AppImage
    PACKAGE_TYPE = PackageType.AppImage

# OS Release info
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
