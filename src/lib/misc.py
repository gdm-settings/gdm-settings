import os
import subprocess


__all__ = ['get_stdout', 'list_files']


def get_stdout(command, /, *, decode=True):
    '''get standard output of a command'''

    if isinstance(command, str):
        command = command.split()

    stdout = subprocess.run(command, stdout=subprocess.PIPE).stdout

    if decode:
        stdout = stdout.decode()

    return stdout


def list_files(dir_path, base=None, *, recursive=True):
    """list files (only) inside a directory"""

    if base is None:
        base = dir_path

    for child in os.listdir(dir_path):
        child_path = os.path.join(dir_path, child)

        if not os.path.isdir(child_path):
            yield os.path.relpath(child_path, base)
        elif recursive:
            yield from list_files(child_path, base)
