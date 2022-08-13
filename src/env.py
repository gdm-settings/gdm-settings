'''get information about program's environment'''

import os
from .utils import PATH

# XDG Base Directories
from gi.repository import GLib
XDG_CONFIG_HOME = GLib.get_user_config_dir()
XDG_RUNTIME_DIR = GLib.get_user_runtime_dir()

# Application-specific Directories
from .info import application_id
TEMP_DIR       = os.path.join(XDG_RUNTIME_DIR, 'app', application_id)
HOST_DATA_DIRS = PATH(os.environ.get('HOST_DATA_DIRS', '/usr/local/share:/usr/share'))

# Package Type and related stuff
from .enums import PackageType
PACKAGE_TYPE = PackageType.Unknown
HOST_ROOT    = ''

if os.environ.get('FLATPAK_ID'): # Flatpak
    PACKAGE_TYPE = PackageType.Flatpak
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
