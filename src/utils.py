'''Some random utility functions, classes, objects, etc. used throughout the source code'''

def getstdout(args):
    from subprocess import run
    if isinstance(args, str):
        args = args.split()
    return run(args, capture_output=True).stdout

def find_file(file, locations):
    from os import path
    found_path = ''
    for location in locations:
        file_path = path.join(location, file.lstrip('/'))
        if path.exists(file_path):
            found_path = file_path
            break
    return found_path

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
