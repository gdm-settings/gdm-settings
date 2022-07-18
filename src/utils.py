'''Some random utility functions, classes, objects, etc. used throughout the source code'''

def getstdout(command, /):
    '''get standard output of a command'''

    from subprocess import run
    if isinstance(command, str):
        command = command.split()
    return run(command, capture_output=True).stdout

def find_file(file, locations):
    '''find a file in possible locations'''

    from os import path
    for location in locations:
        file_path = path.join(location, file.lstrip('/'))
        if path.exists(file_path):
            return file_path

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

def read_os_release():
    filename = None
    from os import path
    for fn in '/run/host/os-release', '/etc/os-release', '/usr/lib/os-release':
        if path.isfile(fn):
            filename = fn
            break

    if filename is None:
        return

    os_release = []
    with open(filename, 'r') as file:
        for line_number, line in enumerate(file, start=1):
            line = line.split('#')[0]   # Discard comments
            line = line.strip()         # Strip whitespace

            if not line:
                continue

            import re
            if m := re.match(r'([A-Z][A-Z_0-9]+)=(.*)', line):
                name, val = m.groups()
                if val and val[0] in '"\'':
                    import ast
                    val = ast.literal_eval(val)
                os_release.append((name, val))
            else:
                import sys
                print(f'{filename}:{line_number}: bad line {line!r}',
                      file=sys.stderr)

    return dict(os_release)


class PATH (list):
    '''
    A list to store values of PATH-like environment variables

    For example, with
        mypath = PATH('/usr/local/bin:/usr/bin')
    OR
        mypath = PATH(['/usr/local/bin', '/usr/bin'])
    we get,
        print(mypath)       # prints /usr/local/bin:/usr/bin
        print(*mypath)      # prints /usr/local/bin /usr/bin
        print(mypath[0])    # prints /usr/local/bin
        print(repr(mypath)) # prints PATH(['/usr/local/bin', '/usr/bin'])
    '''

    def __init__ (self, value=None, /):
        if value is None:
            return list.__init__(self)
        elif isinstance(value, str):
            value = value.strip(':').split(':')
        return list.__init__(self, value)

    def __str__ (self, /):
        return ':'.join(self)

    def __repr__ (self, /):
        return self.__class__.__name__ + '(' + list.__repr__(self) + ')'

    def copy (self, /):
        return self.__class__(self)


class CommandElevator:
    """ Runs a list of commands with elevated privilages """
    def __init__(self, elevator:str='', *, shebang:str='') -> None:
        self.__list = []
        self.shebang = shebang or "#!/bin/sh"
        if elevator:
            self.elevator = elevator
        else:
            self.autodetect_elevator()

    @property
    def shebang(self):
        """ Shebang to determine shell for running elevated commands """
        return self.__shebang
    @shebang.setter
    def shebang(self, value):
        if value.startswith('#!/'):
            self.__shebang = value
        else:
            raise ValueError("shebang does not start with '#!/'")

    @property
    def elevator(self):
        """
        Program to use for privilage elevation

        Example: "sudo", "doas", "pkexec", etc.
        """
        return self.__elevator
    @elevator.setter
    def elevator(self, value):
        if isinstance(value, str):
            self.__elevator = value.strip(' ').split(' ')
        elif isinstance(value, list):
            self.__elevator = value
        else:
            raise ValueError("elevator is not of type 'str' or 'list'")

    def autodetect_elevator(self):
        from .enums import PackageType
        from . import env
        if env.PACKAGE_TYPE is PackageType.Flatpak:
            self.elevator = "flatpak-spawn --host pkexec"
        else:
            self.elevator = "pkexec"

    def add(self, cmd:str, /):
        """ Add a new command to the list """
        return self.__list.append(cmd)

    def clear(self):
        """ Clear command list """
        return self.__list.clear()

    def run_only(self) -> bool:
        """ Run commands but DO NOT clear command list """

        from os import chmod, makedirs, remove
        from subprocess import run
        from . import env

        returncode = 0
        if len(self.__list):
            makedirs(name=env.TEMP_DIR, exist_ok=True)
            script_file = f"{env.TEMP_DIR}/run-elevated"
            with open(script_file, "w") as open_script_file:
                print(self.__shebang, *self.__list, sep="\n", file=open_script_file)
            chmod(path=script_file, mode=755)
            returncode = run(args=[*self.__elevator, script_file]).returncode
            remove(script_file)
        # Return Code 0 of subprocess means success, but boolean with value 0 is interpreted as False
        # So, 'not returncode' boolean will be True when the subprocess succeeds
        return not returncode

    def run(self) -> bool:
        """ Run commands and clear command list"""
        status = self.run_only()
        self.clear()
        return status
