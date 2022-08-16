import os
from gi.repository import Adw, Gtk, Gio
from gettext import gettext as _, pgettext as C_
from .info import data_dir, application_id
from .bind_utils import bind_comborow_by_list

class PreferencesWindow (Adw.PreferencesWindow):
    def __init__ (self, **kwargs):
        super().__init__(title=_('App Preferences'), **kwargs)

        self.builder = Gtk.Builder.new_from_file(os.path.join(data_dir, 'prefs.ui'))

        self.page1 = self.builder.get_object('page1')
        self.info_label = self.builder.get_object('info_label')
        self.overlay_comborow = self.builder.get_object('overlay_comborow')

        text = self.info_label.get_label()
        address = 'https://github.com/realmazharhussain/gdm-settings/wiki'
        self.info_label.set_label(text.format(url=address))

        self.add(self.page1)

        self.bind_to_gsettings()

    def bind_to_gsettings (self):
        self.settings = Gio.Settings.new(application_id)
        bind_comborow_by_list(self.overlay_comborow, self.settings, 'shell-theme-overlay',
                              ['nothing', 'resources', 'everything'])
