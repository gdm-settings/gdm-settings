import os
from gi.repository import Adw, Gtk
from gettext import gettext as _, pgettext as C_
from ..env import TEMP_DIR
from ..info import data_dir, application_id
from ..utils import CommandElevator, BackgroundTask
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

        self.extract_theme_task = BackgroundTask(self.extract_shell_theme, self.on_extract_shell_theme_finish)
        self.window.task_counter.register(self.extract_shell_theme_button)
        self.extract_shell_theme_button.connect('clicked', self.on_extract_shell_theme)

        # Bind to GSettings
        self.gsettings = Gio.Settings.new(f"{application_id}.tools")
        bind(self.gsettings, 'top-bar-tweaks', self.top_bar_tweaks_switch, 'active')

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
        if self.gsettings['top-bar-tweaks']:
            with open(os.path.join(temp_theme_path, 'gnome-shell', 'gnome-shell.css'), 'a') as shell_css:
                shell_css.write(self.window.application.settings_manager.get_setting_css())

        # Copy extracted theme to its permanent path
        command_elevator = CommandElevator()
        command_elevator.add(f'cp -rfT {temp_theme_path} {perm_theme_path}')
        status = command_elevator.run()

        return status, perm_theme_name

    def extract_shell_theme_async(self, callback):
        '''Run apply_settings asynchronously'''

        task = Gio.Task.new(self, None, callback, None)
        task.set_return_on_cancel(False)

        task.run_in_thread(self._extract_shell_theme_thread_callback)

    def _extract_shell_theme_thread_callback(self, task, source_object, task_data, cancellable):
        '''Called by apply_settings_async to run apply_settings in a separate thread'''

        if task.return_error_if_cancelled():
            return

        try:
            value = self.extract_shell_theme()
            task.return_value(value)
        except Exception as e:
            task.return_value(e)

    def extract_shell_theme_finish(self, result):
        '''Returns result(return value) of apply_settings_async'''

        if not Gio.Task.is_valid(result, self):
            from .utils import ProcessReturnCode
            return ProcessReturnCode(-1)

        value = result.propagate_value().value

        if isinstance(value, Exception):
            raise value

        return value
