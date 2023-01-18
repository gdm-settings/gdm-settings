'''Contains info about themes'''

from os import path
from glob import glob
from gettext import pgettext as C_

from gi.repository import GLib

from .env import HOST_ROOT, HOST_DATA_DIRS

class ThemeListBase():
    '''base class for theme lists'''

    def __init__ (self, *args, **kwargs):
        self._dict = dict(*args, **kwargs)
        self.update()

    def __getitem__ (self, theme_id):
        return self._dict[theme_id]

    def __iter__ (self):
        for theme_id in self.theme_ids:
            name, path = self._dict[theme_id]
            yield theme_id, name, path

    @property
    def theme_ids (self):
        case_insensitive_name = lambda theme_id: self.get_name(theme_id).lower()
        return sorted(self._dict, key=case_insensitive_name)

    @property
    def names (self):
        for theme_id, name, path in self:
            yield name

    @property
    def paths (self):
        for theme_id, name, path in self:
            yield path

    def clear (self):
        self._dict.clear()

    def add (self, theme_id, name, path):
        self._dict[theme_id] = (name, path)

    def remove (self, theme_id):
        self._dict.remove(theme_id)

    def get_path (self, theme_id):
        name, path = self._dict.get(theme_id, (None, None))
        return path

    def get_name (self, theme_id):
        name, path = self._dict.get(theme_id, (None, None))
        return name

    def _detect_name(self, theme_dir):
        filename = path.join(theme_dir, 'index.theme')
        if not path.exists(filename):
            return

        theme_file = GLib.KeyFile()
        try:
            theme_file.load_from_file(filename,
                                      GLib.KeyFileFlags.KEEP_TRANSLATIONS)
        except Exception:
            logging.debug(f"Failed to parse '{filename}'!")
            return

        for group in theme_file.get_groups()[0]:
            if 'Name' in theme_file.get_keys(group)[0]:
                return theme_file.get_locale_string(group, 'Name')

    def update (self):
        self.clear()

        for data_dir in HOST_DATA_DIRS:
            for theme_dir in glob(f"{HOST_ROOT}{data_dir}/{self.dirname}/*"):
                theme_id = path.basename(theme_dir)
                theme_name = self._detect_name(theme_dir) or theme_id
                if not path.exists(path.join(theme_dir, self.decider)) or theme_id in self.theme_ids:
                    continue
                self.add(theme_id, theme_name, theme_dir)


class ShellThemes (ThemeListBase):
    def __init__ (self, *args, **kwargs):
        self.dirname = 'themes'
        self.decider = 'gnome-shell'
        super().__init__(*args, **kwargs)

    def update (self):
        super().update()
        self.add('default', C_('Theme Name', 'Default'), None)

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
