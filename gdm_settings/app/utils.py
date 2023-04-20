'''Some random utility functions, classes, objects, etc. used throughout the source code'''

import subprocess

from gdm_settings import resource_base_path
from .enums import PackageType
from . import env


def resource_path (resource_name):
    return resource_base_path + resource_name


def run_on_host(command, *args, **kwargs):
    if isinstance(command, str):
        command = [command]

    if env.PACKAGE_TYPE is PackageType.Flatpak:
        command = ['flatpak-spawn', '--host'] + command

    return subprocess.run(command, *args, **kwargs)
