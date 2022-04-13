import builtins

def set_value(name, obj):
    builtins.__dict__[name] = obj

class PATH:
    '''stores value of a PATH-like variable and provides easy functionality for it.

    For example, with `mypath=PATH('/usr/local/bin:/usr/bin')` OR `mypath=PATH(['/usr/local/bin', '/usr/bin'])`,
    print(mypath)      # prints PATH['/usr/local/bin', '/usr/bin']
    print(str(mypath)) # prints '/usr/local/bin:/usr/bin'
    print(*mypath)     # prints '/usr/local/bin\\n/usr/bin'
    print(mypath[1])   # prints '/usr/bin'
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

    def __repr__(self):
        return f"PATH{self.val}"

    def __str__(self):
        return str.join(':', self.val)

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
