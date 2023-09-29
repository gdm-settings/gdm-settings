import os
import subprocess
from collections.abc import Sequence


from gdms.env import TEMP_DIR, PACKAGE_TYPE
from gdms.enums import PackageType


def _unpack_args(args: tuple):
    # Validate Args
    if len(args) == 0:
        raise ValueError('No argument provided')

    # Unpack Args
    if len(args) == 1:
        return args[0]
    
    return args


class CommandResult(subprocess.CompletedProcess):
    '''Result of a command's execution
    
    Returned by Command.run()
    
    Allows usage patterns like

        if Command('echo "Hello, World!"').run():
            print("Mission accomplished!")

        if Command('which non-existant-program').run().failure:
            print("'non-existant-program' does not exist!")
    '''

    def __init__(self, other: subprocess.CompletedProcess, /):
        super().__init__(args=other.args, returncode=other.returncode,
                         stdout=other.stdout, stderr=other.stderr)

    @property
    def success(self):
        return self.returncode == 0

    @property
    def failure(self):
        return not self.success

    def __bool__ (self):
        return self.success


class Command:
    '''A command-line command'''

    __slots__ = ['_data']
    __dict__ = None

    def __new__(cls, *args: tuple[str] | str):
        args = _unpack_args(args)

        # Create instance
        self = object.__new__(cls)

        # Initialize instance
        if isinstance(args, str):
            self._data = args
        else:
            self._data = [str(arg) for arg in args]

        return self
    
    def __str__(self) -> str:
        if isinstance(self._data, str):
            return self._data
        return ' '.join(repr(segment) for segment in self._data)

    def prefix(self, *prefix: str):
        command = self._data
        if isinstance(command, str):
            command = ' '.join([*prefix, command])
        else:
            command = [*prefix, *command]
        return type(self)(command)

    def _run(self, *args, **kwargs):
        proc = subprocess.run(self._data, *args, shell=isinstance(self._data, str), **kwargs)
        return CommandResult(proc)

    def run(self, *args, as_root=False, escape_sandbox=True, **kwargs):
        command = self

        if as_root:
            command = command.prefix('pkexec')

        if escape_sandbox and PACKAGE_TYPE is PackageType.Flatpak:
            command = command.prefix('flatpak-spawn', '--host')

        return command._run(*args, **kwargs)


class CommandList:
    """A list of commands"""

    def __init__(self, *, initial_list: Sequence[Command] = []):
        self._list = list(initial_list)
    
    def __str__(self):
        return '\n'.join(str(command) for command in self._list)

    @property
    def empty (self):
        return len(self._list) == 0

    def add(self, *command: Command | tuple[str] | str) -> Command:
        """ Add a new command to the list """
        command = _unpack_args(command)

        if not isinstance(command, Command):
            command = Command(command)

        self._list.append(command)

        return command

    def clear(self):
        """ Clear command list """
        self._list.clear()

    def save_to_file(self, filepath: str):
        filedir = os.path.dirname(filepath)
        os.makedirs(filedir, exist_ok=True)

        with open(filepath, "w") as f:
            f.write(str(self))

    def run(self, *args, as_root=True, stop_on_error=True, clear_on_finish=True, **kwargs):
        '''Run commands as root and clear the list'''

        script_path = f"{TEMP_DIR}/run-elevated"
        self.save_to_file(script_path)

        sh_args = []
        if stop_on_error:
            sh_args.append('-e')

        proc = Command('sh', *sh_args, script_path).run(*args, as_root=as_root, **kwargs)
        os.remove(script_path)

        if clear_on_finish:
            self.clear()

        return proc
