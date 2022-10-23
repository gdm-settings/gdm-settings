'''Some random utility functions, classes, objects, etc. used throughout the source code'''

from .enums import PackageType
from . import env

def getstdout(command, /):
    '''get standard output of a command'''

    from subprocess import run, PIPE
    if isinstance(command, str):
        command = command.split()
    return run(command, stdout=PIPE).stdout

def listdir_recursive(directory):
    """list files (only) inside a directory recursively"""

    from os import listdir, path

    files=[]
    for file in listdir(directory):
        if path.isdir(path.join(directory, file)):
            for subdir_file in listdir_recursive(path.join(directory, file)):
                files += [path.join(file, subdir_file)]
        else:
            files += [file]

    return files


def version(string, /):
    '''Return a tuple that represents a program version number'''

    return tuple(int(segment) for segment in string.split('.'))


def run_on_host(command, *args, **kwargs):
    from subprocess import run

    if isinstance(command, str):
        command = [command]
    if env.PACKAGE_TYPE is PackageType.Flatpak:
        command = ['flatpak-spawn', '--host'] + command

    return run(command, *args, **kwargs)


class ProcessReturnCode(int):
    '''
    An integer that represents return code of a process

    bool(instance) returns True if value of instance is 0
    '''

    def __bool__ (self):
        return True if self == 0 else False

    @property
    def success (self):
        return bool(self)

    @property
    def failure (self):
        return not self.success

class NoCommandsFoundError(Exception): pass

class CommandElevator:
    """ Runs a list of commands with elevated privileges """
    def __init__(self, *, shebang='#!/bin/sh') -> None:
        self._list = []
        self.shebang = shebang

    @property
    def empty (self):
        return True if len(self._list) == 0 else False

    def add(self, command, /):
        """ Add a new command to the list """

        if isinstance(command, list):
            command = ' '.join(command)

        return self._list.append(command)

    def clear(self):
        """ Clear command list """
        return self._list.clear()

    def run_only(self) -> bool:
        """ Run commands but DO NOT clear command list """

        from os import chmod, makedirs, remove
        from subprocess import run

        returncode = 0
        if len(self._list):
            makedirs(name=env.TEMP_DIR, exist_ok=True)
            script_file = f"{env.TEMP_DIR}/run-elevated"
            with open(script_file, "w") as open_script_file:
                print(self.shebang, *self._list, sep="\n", file=open_script_file)
            chmod(path=script_file, mode=0o755)
            returncode = run_on_host(['pkexec', script_file]).returncode
            remove(script_file)

        return ProcessReturnCode(returncode)

    def run(self) -> bool:
        """ Run commands and clear command list"""

        if self.empty:
            raise NoCommandsFoundError(1, f'{self.__class__.__name__} instance has no commands to run')

        status = self.run_only()
        self.clear()
        return status


class InvalidGioTaskError (Exception): pass
class AlreadyRunningError (Exception): pass

from gi.repository import Gio, GObject

class BackgroundTask (GObject.Object):
    __gtype_name__ = 'BackgroundTask'

    def __init__ (self, function, finish_callback, **kwargs):
        super().__init__(**kwargs)

        self.function = function
        self.finish_callback = finish_callback
        self._current = None

    def start(self):
        if self._current:
            AlreadyRunningError('Task is already running')

        finish_callback = lambda self, task, nothing: self.finish_callback()

        task = Gio.Task.new(self, None, finish_callback, None)
        task.run_in_thread(self._thread_cb)

        self._current = task

    @staticmethod
    def _thread_cb (task, self, task_data, cancellable):
        try:
            retval = self.function()
            task.return_value(retval)
        except Exception as e:
            task.return_value(e)

    def finish (self):
        task = self._current
        self._current = None

        if not Gio.Task.is_valid(task, self):
            raise InvalidGioTaskError()

        value = task.propagate_value().value

        if isinstance(value, Exception):
            raise value

        return value
