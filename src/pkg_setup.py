from os import environ as env
import builtins

def install(name, obj):
    builtins.__dict__[name] = obj

install('PACKAGE_TYPE', None)
install('HOST_ROOT',    '')

if env.get('FLATPAK_ID'): # Flatpak
    install('PACKAGE_TYPE', 'Flatpak')
    install('HOST_ROOT',    '/var/run/host')

elif env.get('APPDIR'):   # AppImage
    install('PACKAGE_TYPE', 'AppImage')
