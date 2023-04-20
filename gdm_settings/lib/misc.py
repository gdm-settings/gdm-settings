import os
import subprocess

from typing import Optional
from collections.abc import Iterator

from gi.repository import GObject


__all__ = ['get_stdout', 'list_files', 'GProperty']


def GProperty(type: GObject.GType,
              default: Optional[object] = None,
              *args,
              readable: bool = True,
              writable: bool = True,
              construct: bool = False,
              construct_only: bool = False,
              additional_flags: GObject.ParamFlags = GObject.ParamFlags(0),
              **kwargs,
              ) -> GObject.Property:
    '''A wrapper around GObject.Property decorator

    Provides shorter syntax for creating GObject properties.
    '''

    flags = additional_flags
    if readable:
        flags |= GObject.ParamFlags.READABLE
    if writable:
        flags |= GObject.ParamFlags.WRITABLE
    if construct:
        flags |= GObject.ParamFlags.CONSTRUCT
    if construct_only:
        flags |= GObject.ParamFlags.CONSTRUCT_ONLY

    return GObject.Property(*args, type=type, default=default, flags=flags, **kwargs)


def get_stdout(command: str | list [str],
               /, *,
               decode: bool = True,
               ) -> str | bytes:
    '''get standard output of a command'''

    if isinstance(command, str):
        command = command.split()

    stdout = subprocess.run(command, stdout=subprocess.PIPE).stdout

    if decode:
        stdout = stdout.decode()

    return stdout


def list_files(dir_path: str,
               base: Optional[str] = None,
               *,
               recursive: bool = True,
               ) -> Iterator[str]:
    """list files (only) inside a directory"""

    if base is None:
        base = dir_path

    for child in os.listdir(dir_path):
        child_path = os.path.join(dir_path, child)

        if not os.path.isdir(child_path):
            yield os.path.relpath(child_path, base)
        elif recursive:
            yield from list_files(child_path, base)
