'''Some random utility functions, classes, objects, etc. used throughout the source code'''

import subprocess

from .enums import PackageType
from . import env


def run_on_host(command, *args, **kwargs):
    if isinstance(command, str):
        command = [command]

    if env.PACKAGE_TYPE is PackageType.Flatpak:
        command = ['flatpak-spawn', '--host'] + command

    return subprocess.run(command, *args, **kwargs)
