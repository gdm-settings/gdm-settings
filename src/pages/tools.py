import os
from gi.repository import Gtk
from ..utils import CommandElevator
from ..info import data_dir, application_id
from ..gr_utils import extract_default_theme, ThemesDir
from ..bind_utils import *
from .common import PageContent


class ToolsPageContent (PageContent):
    __gtype_name__ = 'ToolsPageContent'

    def __init__ (self, window, **kwargs):
        super().__init__(**kwargs)

        self.window = window

        self.builder = Gtk.Builder.new_from_file(os.path.join(data_dir, 'tools-page.ui'))

        self.set_child(self.builder.get_object('content_box'))

        self.top_bar_tweaks_switch = self.builder.get_object('top_bar_tweaks_switch')
        self.extract_shell_theme_button = self.builder.get_object('extract_shell_theme_button')

        self.extract_shell_theme_button.connect('clicked', self.on_extract_shell_theme)

        # Bind to GSettings
        self.gsettings = Gio.Settings.new(f"{application_id}.tools")
        bind(self.gsettings, 'top-bar-tweaks', self.top_bar_tweaks_switch, 'active')

    def on_extract_shell_theme(self, button):

        perm_theme_name = 'default-extracted'
        perm_theme_path = join(ThemesDir, perm_theme_name)
        temp_theme_path = join(env.TEMP_DIR, 'extracted-theme')

        # Extract default shell theme to a temporary path
        extract_default_theme(temp_theme_path)

        # If enabled, apply top bar tweaks
        if self.gsettings['top-bar-tweaks']:
            with open(join(temp_theme_path, 'gnome-shell', 'gnome-shell.css'), 'a') as shell_css:
                shell_css.write(self.window.application.settings_manager.get_setting_css())

        # Copy extracted theme to its permanent path
        command_elevator = CommandElevator()
        command_elevator.add(f'cp -rfT {temp_theme_path} {perm_theme_path}')
        status = command_elevator.run()

        # Notify the user via in-app notification
        if status.success:
            # Translators: Do not translate '{folder}' and '{name}'. Keep these as they are.
            # They will be replaced by an actual folder path and theme name during runtime.
            msg = _("Default shell theme extracted to '{folder}' as '{name}'")
            message = msg.format(folder=ThemesDir, name=perm_theme_name)
        else:
            message = _("Failed to extract default theme")
        toast = Adw.Toast(timeout=2, priority="high", title=message)
        self.window.toast_overlay.add_toast(toast)
