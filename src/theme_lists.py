'''Contains info about themes'''

from os import path
from glob import glob
from .env import HOST_ROOT, HOST_DATA_DIRS

class ThemeListBase():
    '''base class for theme lists'''

    def __init__ (self, *args, **kwargs):
        self._dict = dict(*args, **kwargs)
        self.update()

    def __getitem__ (self, name):
        return self._dict[name]

    def __iter__ (self):
        for name in self.names:
            path = self._dict[name]
            yield name, path

    @property
    def names (self):
        return sorted(self._dict, key=str.lower)

    def clear (self):
        self._dict.clear()

    def add (self, name, path):
        self._dict[name] = path

    def remove (self, name):
        self._dict.remove(name)

    def get_path (self, name):
        return self._dict.get(name, None)

    def update (self):
        self.clear()

        for data_dir in HOST_DATA_DIRS:
            for theme_dir in glob(f"{HOST_ROOT}{data_dir}/{self.dirname}/*"):
                theme_name = path.basename(theme_dir)
                if path.exists(path.join(theme_dir, self.decider)) and theme_name not in self.names:
                    self.add(theme_name, theme_dir)

class ShellThemes (ThemeListBase):
    def __init__ (self, *args, **kwargs):
        self.dirname = 'themes'
        self.decider = 'gnome-shell'
        super().__init__(*args, **kwargs)

    def update (self):
        super().update()
        self.add('default', None)

class SoundThemes (ThemeListBase):
    def __init__ (self, *args, **kwargs):
        self.dirname = 'sounds'
        self.decider = 'index.theme'
        super().__init__(*args, **kwargs)

class IconThemes (ThemeListBase):
    def __init__ (self, *args, **kwargs):
        self.dirname = 'icons'
        self.decider = 'index.theme'
        super().__init__(*args, **kwargs)

class CursorThemes (ThemeListBase):
    def __init__ (self, *args, **kwargs):
        self.dirname = 'icons'
        self.decider = 'cursors'
        super().__init__(*args, **kwargs)

shell_themes  = ShellThemes()
sound_themes  = SoundThemes()
icon_themes   = IconThemes()
cursor_themes = CursorThemes()
