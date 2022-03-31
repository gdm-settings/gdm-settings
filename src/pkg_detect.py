#!/usr/bin/env python3
from os import environ as env
import builtins

def install(name, obj):
    builtins.__dict__[name] = obj

def append_env(var, val, default=''):
    env.update({var: env.get(var, default) + val})

if env.get('FLATPAK_ID'): # Flatpak
    host_data_dir = ':/var/run/host/usr/share'
    append_env('XDG_DATA_DIRS', ':' + host_data_dir)
elif env.get('APPDIR'):   # AppImage
    pass
