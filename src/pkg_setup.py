from os import environ as env
from .utils import set_value

set_value('PACKAGE_TYPE', None)
set_value('HOST_ROOT',    '')

if env.get('FLATPAK_ID'): # Flatpak
    set_value('PACKAGE_TYPE', 'Flatpak')
    set_value('HOST_ROOT',    '/var/run/host')

elif env.get('APPDIR'):   # AppImage
    set_value('PACKAGE_TYPE', 'AppImage')
