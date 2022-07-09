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

class PATH:
    '''Iterable PATH-like variable.

    For example, with
        mypath = PATH('/usr/local/bin:/usr/bin')
    OR
        mypath = PATH(['/usr/local/bin', '/usr/bin'])
    we get,
        print(mypath)       # prints /usr/local/bin:/usr/bin
        print(*mypath)      # prints /usr/local/bin /usr/bin
        print(mypath[0])    # prints /usr/local/bin
        print(repr(mypath)) # prints PATH('/usr/local/bin:/usr/bin')
    '''
    def __init__(self, val=[], /):
        if isinstance(val, list):
            self.val = val.copy()
        elif isinstance(val, str):
            self.val = val.strip(':').split(':')
        elif val is None:
            self.val = []
        else:
            raise ValueError("provided value is not of type 'str' or 'list'.")

    def __str__(self):
        return str.join(':', self.val)

    def __repr__(self):
        return self.__class__.__name__ + '(' + self.__str__().__repr__() + ')'

    def __iter__(self):
        for item in self.val:
            yield item

    def __getitem__(self, subscript, /):
        return self.val[subscript]

    def copy(self):
        return self.__class__(self.val)

    def prefix(self, prefix, /):
        self.val = [prefix+item for item in self.val]
        return True

    def postfix(self, postfix, /):
        self.val = [item+postfix for item in self.val]
        return True

    def insert(self, position, value):
        return self.val.insert(position, value)

    def append(self, val, /):
        return self.val.append(val)

    def prepend(self, val, /):
        return self.val.insert(0, val)
