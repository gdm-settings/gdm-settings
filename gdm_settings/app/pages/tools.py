import os
from gettext import gettext as _

from gi.repository import Adw, Gtk

from gdm_settings import APP_ID
from gdm_settings.env import TEMP_DIR
from gdm_settings.cmd import Command
from gdm_settings.utils import BackgroundTask, GSettings
from gdm_settings.widgets import SwitchRow

from ..gr_utils import extract_default_theme, ThemesDir
from .common import PageContent


class ToolsPageContent (PageContent):
    __gtype_name__ = 'ToolsPageContent'

    def __init__ (self, window, **props):
        super().__init__(**props)

        self.window = window

        self.builder = Gtk.Builder.new_from_resource('/app/ui/tools-page.ui')

        self.set_child(self.builder.get_object('content_box'))

        self.top_bar_tweaks_row = self.builder.get_object('top_bar_tweaks_row')
        self.extract_shell_theme_button = self.builder.get_object('extract_shell_theme_button')

        self.extract_theme_task = BackgroundTask(self.extract_shell_theme, self.on_extract_shell_theme_finish)
        self.window.task_counter.register(self.extract_shell_theme_button)
        self.extract_shell_theme_button.connect('clicked', self.on_extract_shell_theme)

        # Bind to GSettings
        self.settings = GSettings(APP_ID + '.tools')
        self.settings.bind('top-bar-tweaks', self.top_bar_tweaks_row, 'enabled')

    def on_extract_shell_theme(self, button):
        self.window.task_counter.inc()
        self.extract_theme_task.start()

    def on_extract_shell_theme_finish(self):
        status, theme_name = self.extract_theme_task.finish()
        self.window.task_counter.dec()

        if status.success:
            # Translators: Do not translate '{folder}' and '{name}'. Keep these as they are.
            # They will be replaced by an actual folder path and theme name during runtime.
            msg = _("Default shell theme extracted to '{folder}' as '{name}'")
            message = msg.format(folder=ThemesDir, name=theme_name)
        else:
            message = _("Failed to extract default theme")
        toast = Adw.Toast(timeout=2, priority="high", title=message)
        self.window.toast_overlay.add_toast(toast)

    def extract_shell_theme (self):
        perm_theme_name = 'default-extracted'
        perm_theme_path = os.path.join(ThemesDir, perm_theme_name)
        temp_theme_path = os.path.join(TEMP_DIR, 'extracted-theme')

        # Extract default shell theme to a temporary path
        extract_default_theme(temp_theme_path)

        # If enabled, apply top bar tweaks
        if self.settings['top-bar-tweaks']:
            with open(os.path.join(temp_theme_path, 'gnome-shell', 'gnome-shell.css'), 'a') as shell_css:
                shell_css.write(self.window.application.settings_manager.get_setting_css())

        # Copy extracted theme to its permanent path
        cmd = Command('cp', '-rfT', temp_theme_path, perm_theme_path)
        res = cmd.run(as_root=True)

        return res, perm_theme_name
