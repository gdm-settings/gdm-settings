'''Some random utility functions, classes, objects, etc. used throughout the source code'''

def getstdout(args):
    from subprocess import run
    if isinstance(args, str):
        args = args.split()
    return run(args, capture_output=True).stdout

def find_file(file, locations):
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
    import os

    filename = None
    for fn in '/run/host/os-release', '/etc/os-release', '/usr/lib/os-release':
        if os.path.isfile(fn):
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
