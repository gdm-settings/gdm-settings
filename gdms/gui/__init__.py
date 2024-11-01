'''Contains the main Application class'''

import sys
import logging
import subprocess
from configparser import ParsingError
from gettext import gettext as _, pgettext as C_

from gi.repository import Gio, GLib
from gi.repository import Adw, Gtk, Gdk

from gdms import APP_NAME, APP_ID, VERSION, APP_DATA_DIR
from gdms import stderr_log_handler
from gdms import env
from gdms.enums import PackageType
from gdms.utils import BackgroundTask, GSettings
from gdms import gresource
from gdms import debug_info
from gdms import settings

Gio.Resource.load(APP_DATA_DIR + '/resources.gresource')._register()

from .about import about_window
from .window import GdmSettingsWindow

logger = logging.getLogger(__name__)


def set_logging_level(verbosity):
    # Logging Levels are integers with following values
    # logging.CRITICAL = 50
    # logging.ERROR    = 40
    # logging.WARNING  = 30
    # logging.INFO     = 20
    # logging.DEBUG    = 10
    # and integer values above 50 disable logging completely
    # But this is what the values of our app's --verbosity option represent
    # 0 = DISABLE, 1 = CRITICAL, 2 = ERROR, 3 = WARNING, 4 = INFO, 5 = DEBUG
    # So, we use following formula to get appropriate integer that represents chosen level
    # For example, with --verbosity=0 we get, (6-verbosity)*10 = (6-0)*10 = 6*10 = 60 (no logging)
    #            , with --verbosity=1 we get, (6-verbosity)*10 = (6-1)*10 = 5*10 = 50 = logging.CRITICAL
    #         And, with --verbosity=5 we get, (6-verbosity)*10 = (6-5)*10 = 1*10 = 10 = logging.DEBUG
    level = (6 - verbosity) * 10
    stderr_log_handler.setLevel(level)


class GdmSettingsApp(Adw.Application):
    '''The main Application class'''

    __gtype_name__ = "GdmSettingsApp"

    def __init__(self):
        super().__init__(application_id=APP_ID)
        self.props.resource_base_path = '/app/'

        def add_option(long_name, short_name, description, argument_name=None, argument_type='NONE'):
            self.add_main_option(long_name, ord(short_name),
                                 GLib.OptionFlags.NONE,
                                 getattr(GLib.OptionArg, argument_type),
                                 description, argument_name,
                                 )

        add_option('debug-info', 'i',  _('Show debug information (in Markdown format)'))
        add_option('version',    '\0', _('Show application version'))
        add_option('verbosity',  '\0', _('Set verbosity level manually (from 0 to 5)'),
                   C_('Argument of --verbosity option', 'LEVEL'), 'INT')
        add_option('verbose',    'v',  _('Enable verbose mode (alias of --verbosity=5)'))
        add_option('quiet',      'q',  _('Enable quiet mode (alias of --verbosity=0)'))


    def do_handle_local_options(self, options):
        if options.contains("version"):
            print(APP_NAME, VERSION)
            return 0

        if options.contains("debug-info"):
            print(debug_info.as_markdown())
            return 0

        set_logging_level(3)

        if options.contains("verbose"):
            set_logging_level (5)

        if options.contains("quiet"):
            set_logging_level (0)

        if verbosity_gvariant := options.lookup_value("verbosity", GLib.VariantType("i")):
            verbosity_level = verbosity_gvariant.get_int32()

            if verbosity_level < 0 or verbosity_level > 5:
                print(_('Invalid verbosity level {level}. Must be 0, 5, or in-between.'
                       ).format(level=verbosity_level),
                      file=sys.stderr)
                return 1

            set_logging_level(verbosity_level)

        return -1


    def do_startup(self):
        Adw.Application.do_startup(self)
        settings.init()

    def do_activate(self):
        if win := self.get_active_window():
            win.present()
            return

        BOLD = '\033[1m'
        NORMAL = '\033[0m'
        for key, val in debug_info.debug_info:
            logger.info(f"{BOLD}{key}{NORMAL}: {val}")

        self.settings = GSettings(APP_ID)

        self.reset_settings_task = BackgroundTask(settings.reset,
                                                  self.on_reset_settings_finish)

        self.import_task = BackgroundTask(None, self.on_import_finished)
        self.export_task = BackgroundTask(None, self.on_export_finished)

        self.create_actions()
        self.keyboard_shortcuts()

        self.window = GdmSettingsWindow(self)
        self.window.present()

        # Some dependencies cannot be packaged along with the app but are
        # required to be installed on the user's system. So, we need to
        # check them and report to the user if they are missing.
        if not self.check_system_dependencies():
            return

        if not gresource.get_default():
            self.show_missing_gresource_dialog()
            return

        if (not self.settings['donation-dialog-shown']
        and not self.settings['never-applied']):
            self.show_donation_dialog()


    def do_shutdown(self):
        settings.finalize()
        Adw.Application.do_shutdown(self)


    def check_system_dependencies(self):
        '''If some dependencies are missing, show a dialog reporting the situation'''

        def check_dependency(exec_name, logging_name=None, *, on_host=True):
            host_args = []
            if env.PACKAGE_TYPE is PackageType.Flatpak and on_host is True:
                host_args = ['flatpak-spawn', '--host']

            try:
                proc = subprocess.run([*host_args, exec_name, '--version'], capture_output=True)
                if proc.returncode == 0:
                    version_info = proc.stdout.decode().strip()
                    if logging_name:
                        logger.info(f'{logging_name} {version_info}')
                    else:
                        logger.info(version_info)
                    return True
            except FileNotFoundError: pass

            return False

        gdm_installed = bool(gresource.ShellGresourceFile)
        polkit_installed = check_dependency('pkexec')

        if gdm_installed and polkit_installed:
            return True

        if env.PACKAGE_TYPE is PackageType.Flatpak:
            message = _('Following programs are required to be installed <b>on the host system</b> for'
                        ' this app to function properly but they are not installed on the host system.'
                       )
        else:
            message = _('This app requires the following software to function properly but'
                        ' they are not installed.'
                       )

        message += '\n'

        if not gdm_installed:
            message += '\n'
            message += C_('Missing Dependency',
                          '<b>GDM</b>'
                         )

        if not polkit_installed:
            message +='\n'
            message += C_('Missing Dependency',
                          '<b>Polkit</b>'
                         )

        message += '\n\n'

        link = 'https://github.com/gdm-settings/gdm-settings/wiki/Dependencies#how-to-install-dependencies'
        # Translators: Keep '<a href="{url}">' and '</a>' as is. The words between them will become
        # a link to '{url}' and '{url}' will be replaced by a real URL during program execution.
        message += _('Click <a href="{url}">here</a> for instructions on how '
                     'to install these dependencies on your system.'
                    ).format(url=link)

        dialog = Adw.MessageDialog(
                    body = message,
                   modal = True,
                 heading = _('Missing Dependencies'),
           transient_for = self.window,
         body_use_markup = True,
        )

        dialog.add_response('ok', _('OK'))
        dialog.connect('response', lambda *args: self.quit())
        dialog.present()


    def show_missing_gresource_dialog (self):
        heading = _("Default Shell Theme File Lost")
        body = _(
            "The app needs but could not find an unmodified default shell theme file. "
            "To fix the issue, reinstall 'gnome-shell-common' or 'gnome-shell' package."
        )

        dialog = Adw.MessageDialog.new(self.window, heading, body)
        dialog.add_response('ok', _('OK'))
        dialog.connect('response', lambda *args: self.quit())
        dialog.present()


    def show_donation_dialog (self):
        heading = _("Donation Request")
        body = _(
            "If you like this app, please consider donating so that we can keep improving it.\n"
            "Thank you! ❤️️"
        )

        dialog = Adw.AlertDialog.new(heading, body)

        dialog.add_response('close', _("Not Interested"))
        dialog.add_response('donate', _("Donate"))

        dialog.set_response_appearance('donate', Adw.ResponseAppearance.SUGGESTED)
        dialog.set_default_response('donate')

        dialog.connect('response::donate', lambda *args: self.activate_action('donate'))

        dialog.present(self.window)

        self.settings['donation-dialog-shown'] = True


    def keyboard_shortcuts(self):
        self.set_accels_for_action("app.quit", ["<Ctrl>q"])
        self.set_accels_for_action("app.refresh", ["<Ctrl>r", "F5"])


    def create_actions(self):

        def create_action(action_name, function):
            action = Gio.SimpleAction(name=action_name)
            action.connect("activate", function)
            self.add_action(action)

        create_action("refresh", self.refresh_cb)
        create_action("load_session_settings", self.load_session_settings_cb)
        create_action("reset_settings", self.reset_settings_cb)
        create_action("import_from_file", self.import_from_file_cb)
        create_action("export_to_file", self.export_to_file_cb)
        create_action("donate", self.donate_cb)
        create_action("about", self.about_cb)
        create_action("quit", self.quit_cb)


    def refresh_cb(self, action, user_data):
        settings.drop_unapplied_changes()

        toast = Adw.Toast(timeout=1, priority='high', title=_('Settings reloaded'))
        self.window.toast_overlay.add_toast(toast)


    def load_session_settings_cb(self, action, user_data):
        if env.PACKAGE_TYPE is not PackageType.Flatpak:
            settings.load_from_session()
            toast = Adw.Toast(timeout=1, priority='high', title=_('Session settings loaded successfully'))
            self.window.toast_overlay.add_toast(toast)
        else:
            toast = Adw.Toast(timeout=2, priority="high")
            toast.set_title(_("Load session settings is NOT supported in Flatpak version"))
            self.window.toast_overlay.add_toast(toast)


    def reset_settings_cb(self, action, user_data):
        self.window.task_counter.inc()
        self.reset_settings_task.start()

    def on_reset_settings_finish(self):
        success = self.reset_settings_task.finish()
        self.window.task_counter.dec()

        if success:
            message = _("Reset settings successfully")
        else:
            message = _("Failed to reset settings")

        toast = Adw.Toast(timeout=2, priority="high", title=message)
        self.window.toast_overlay.add_toast(toast)


    def import_from_file_cb(self, action, user_data):

        def on_file_chooser_response(file_chooser, response):
            if response == Gtk.ResponseType.ACCEPT:
                self.window.task_counter.inc()
                filepath = file_chooser.get_file().get_path()
                self.import_task.function = lambda: settings.load_from_file(filepath)
                self.import_task.start()
            file_chooser.destroy()

        self._file_chooser = Gtk.FileChooserNative(
                                      modal = True,
                                     action = Gtk.FileChooserAction.OPEN,
                               accept_label = _('Import'),
                              transient_for = self.window,
                             )

        ini_filter = Gtk.FileFilter(name='INI Files')
        ini_filter.add_suffix('ini')
        self._file_chooser.add_filter(ini_filter)
        self._file_chooser.set_filter(ini_filter)

        all_filter = Gtk.FileFilter(name='All Files')
        all_filter.add_pattern('*')
        self._file_chooser.add_filter(all_filter)

        self._file_chooser.connect('response', on_file_chooser_response)
        self._file_chooser.show()

    def on_import_finished(self):
        self.window.task_counter.dec()
        try:
            self.import_task.finish()

            message = _('Settings were successfully imported from file')
        except (ParsingError, UnicodeDecodeError):
            message = _('Failed to import. File is invalid')

        toast = Adw.Toast(timeout=2, priority="high", title=message)
        self.window.toast_overlay.add_toast(toast)


    def export_to_file_cb(self, action, user_data):

        def on_file_chooser_response(file_chooser, response):
            if response == Gtk.ResponseType.ACCEPT:
                self.window.task_counter.inc()
                filepath = file_chooser.get_file().get_path()
                self.export_task.function = lambda: settings.save_to_file(filepath)
                self.export_task.start()
            file_chooser.destroy()

        self._file_chooser = Gtk.FileChooserNative(
                                      modal = True,
                                     action = Gtk.FileChooserAction.SAVE,
                              transient_for = self.window,
                             )

        self._file_chooser.set_current_name('gdm-settings.ini')
        self._file_chooser.connect('response', on_file_chooser_response)
        self._file_chooser.show()

    def on_export_finished(self):
        self.window.task_counter.dec()
        try:
            self.export_task.finish()

            message = _('Settings were successfully exported')
        except PermissionError:
            message = _('Failed to export. Permission denied')
        except IsADirectoryError:
            message = _('Failed to export. A directory with that name already exists')

        toast = Adw.Toast(timeout=2, priority="high", title=message)
        self.window.toast_overlay.add_toast(toast)


    def donate_cb(self, action, user_data):
        Gtk.show_uri(self.window, 'https://opencollective.com/gdm-settings', Gdk.CURRENT_TIME)


    def about_cb(self, action, user_data):
        win = about_window(self.window)
        win.present()


    def quit_cb(self, action, user_data):
        self.quit()
