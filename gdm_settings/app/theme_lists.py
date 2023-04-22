'''Contains info about themes'''

from os import path
from glob import glob
from gettext import pgettext as C_
from dataclasses import dataclass
import logging

from gi.repository import GLib

from gdm_settings.env import HOST_ROOT, HOST_DATA_DIRS


@dataclass
class ThemeInfo:
    theme_id: str
    name: str
    path: str

class ThemeList:
    def __init__(self, dirname, decider, add_default=False):
        self.dirname = dirname
        self.decider = decider
        self.add_default = add_default

        self.update()

    def __iter__(self):
        return self._list.__iter__()

    def __getitem__(self, index):
        return self._list[index]

    def __call__(self, theme_id):
        for theme in self:
            if theme.theme_id == theme_id:
                return theme

    def with_name(self, name):
        filtered_list = []
        for theme in self:
            if theme.name == name:
                filtered_list.append(theme)
        return filtered_list

    def _add(self, theme_id, name, path):
        self._list.append(ThemeInfo(theme_id, name, path))

    def _load_index(self, theme_dir):
        filename = path.join(theme_dir, 'index.theme')
        if not path.exists(filename):
            return

        index_file = GLib.KeyFile()
        try:
            index_file.load_from_file(filename,
                                      GLib.KeyFileFlags.KEEP_TRANSLATIONS)
        except Exception:
            logging.debug(f"Failed to parse '{filename}'!")
            return

        return index_file

    def _get_name(self, index_file):
        if not index_file:
            return
        for group in index_file.get_groups()[0]:
            if 'Name' in index_file.get_keys(group)[0]:
                return index_file.get_locale_string(group, 'Name')

    def _is_theme(self, theme_dir, index_file):
        '''checks if @theme_dir@ contains a valid theme of prefered type'''
        return path.exists(path.join(theme_dir, self.decider))

    def update(self):
        self._list = []

        added_ids=[]
        for data_dir in HOST_DATA_DIRS:
            for theme_dir in glob(f"{HOST_ROOT}{data_dir}/{self.dirname}/*"):
                theme_id = path.basename(theme_dir)
                index_file = self._load_index(theme_dir)
                theme_name = self._get_name(index_file) or theme_id
                if theme_id in added_ids or not self._is_theme(theme_dir, index_file):
                    continue
                self._add(theme_id, theme_name, theme_dir)

        self._list.sort(key = lambda x: x.name.lower())

        if self.add_default:
            self._list.insert(0, ThemeInfo('', C_('Theme Name', 'Default'), None))

    @property
    def theme_ids (self):
        id_list = []
        for theme in self:
            id_list.append(theme.theme_id)
        return id_list

    @property
    def names(self):
        name_list = []
        for theme in self:
            name_list.append(theme.name)
        return name_list

    def get_path(self, theme_id):
        if theme := self(theme_id):
            return theme.path

class IconThemeList(ThemeList):
    def __init__(self):
        super().__init__('icons', None)

    def _is_theme(self, theme_dir, index_file):
        if not index_file:
            return False

        if ('Icon Theme' in index_file.get_groups()[0]
        and 'Directories' in index_file.get_keys('Icon Theme')[0]):
            return True

        return False


icon_themes   = IconThemeList()
shell_themes  = ThemeList('themes', 'gnome-shell', True)
sound_themes  = ThemeList('sounds', 'index.theme')
cursor_themes = ThemeList('icons', 'cursors')
