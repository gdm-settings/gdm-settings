'''Some random utility functions, classes, objects, etc. used throughout the source code'''

from .info import resource_base_path
from .enums import PackageType
from . import env


def resource_path (resource_name):
    return resource_base_path + resource_name


def run_on_host(command, *args, **kwargs):
    from subprocess import run
    if isinstance(command, str):
        command = [command]

    if env.PACKAGE_TYPE is PackageType.Flatpak:
        command = ['flatpak-spawn', '--host'] + command

    return run(command, *args, **kwargs)
