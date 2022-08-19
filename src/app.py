'''Contains the main Application class'''

import sys
import logging
from gettext import gettext as _, pgettext as C_

import gi
gi.require_version("Adw", '1')
from gi.repository import Gio, GLib
from gi.repository import Adw, Gtk

from .settings import SettingsManager
from .window import GdmSettingsWindow
from .gr_utils import ShellGresourceFile, UbuntuGdmGresourceFile
from . import env
from . import info


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
    logging.root.setLevel(level)


class Application(Adw.Application):
    '''The main Application class'''
    def __init__(self):
        super().__init__(application_id=info.application_id)

        def add_option(long_name, short_name, description, argument_name=None):
            self.add_main_option(long_name, ord(short_name),
                                 GLib.OptionFlags.NONE, GLib.OptionArg.NONE,
                                 description, argument_name,
                                 )

        add_option('version',   '\0', _('Show application version'))
        add_option('verbosity', '\0', _('Set verbosity level manually (from 0 to 5)'),
                   C_('Argument of --verbosity option', 'LEVEL'))
        add_option('verbose',   'v',  _('Enable verbose mode (alias of --verbosity=5)'))
        add_option('quiet',     'q',  _('Enable quiet mode (alias of --verbosity=0)'))

        self.connect('shutdown', self.on_shutdown)


    def do_handle_local_options(self, options):
        if options.contains("version"):
            print (info.application_name, f"({info.project_name})", f"v{info.version}")
            return 0

        if options.contains("verbose"):
            set_logging_level (5)

        if options.contains("quiet"):
            set_logging_level (0)

        if verbosity_gvariant := options.lookup_value("verbosity", GLib.VariantType("i")):
            verbosity_level = verbosity_gvariant.get_int32()

            if verbosity_level >= 0 and verbosity_level <= 5:
                set_logging_level (verbosity_level)
            else:
                print(_('{level} is an invalid verbosity level. Accepted values are 0 to 5.\n'
                        'Assuming Verbosity level 4.').format(level=verbosity_level),
                      file=sys.stderr)
                set_logging_level (4)

        return -1


    def do_activate(self):
        if win := self.get_active_window():
            win.present()
            return

        logging.info(f"Application Version    = {info.version}")
        logging.info(f"Operating System       = {env.OS_PRETTY_NAME}")
        logging.info(f"PackageType            = {env.PACKAGE_TYPE.name}")
        logging.info(f"TEMP_DIR               = {env.TEMP_DIR}")
        logging.info(f"HOST_DATA_DIRS         = {env.HOST_DATA_DIRS}")
        logging.info(f"ShellGresourceFile     = {ShellGresourceFile}")
        logging.info(f"UbuntuGdmGresourceFile = {UbuntuGdmGresourceFile}")

        self.settings_manager = SettingsManager()

        self.create_actions()
        self.keyboard_shortcuts()

        self.window = GdmSettingsWindow(self)
        self.window.present()

        # Some dependencies cannot be packaged along with the app but are
        # required to be installed on the user's system. So, we need to
        # check them and report to the user if they are missing.
        self.check_system_dependencies()


    @staticmethod
    def on_shutdown(self):
        self.settings_manager.cleanup()


    def check_system_dependencies(self):
        '''If some dependencies are missing, show a dialog reporting the situation'''

        from subprocess import run
        from .enums import PackageType

        def check_dependency(exec_name, logging_name=None, *, on_host=True):
            host_args = []
            if env.PACKAGE_TYPE is PackageType.Flatpak and on_host is True:
                host_args = ['flatpak-spawn', '--host']

            try:
                proc = run([*host_args, exec_name, '--version'], capture_output=True)
                if proc.returncode == 0:
                    version_info = proc.stdout.decode().strip()
                    if logging_name:
                        logging.info(f'{logging_name} {version_info}')
                    else:
                        logging.info(version_info)
                    return True
            except FileNotFoundError: pass

            return False

        gdm_installed = bool(ShellGresourceFile)
        polkit_installed = check_dependency('pkexec')
        glib_dev_installed = check_dependency('glib-compile-resources', 'GLib', on_host=False)

        host_deps_installed = gdm_installed and polkit_installed
        all_deps_installed = host_deps_installed and glib_dev_installed

        if all_deps_installed:
            return

        message = ''

        if not glib_dev_installed:
            message = _('This app requires the following software to function properly but they are not installed.')
            message += '\n\n'
            message += C_('Missing Dependency',
                          ' • <b>GLib</b> (Developer Edition)'
                         )

        if not host_deps_installed:
            if env.PACKAGE_TYPE == PackageType.Flatpak:
                if not glib_dev_installed:
                    message += '\n\n'

                message += _('Following programs are required to be installed <b>on the host system</b> for'
                             ' this app to function properly but they are not installed on the host system.'
                            ) + '\n'

            if not gdm_installed:
                message += '\n'
                message += C_('Missing Dependency',
                              ' • <b>GDM</b>'
                             )

            if not polkit_installed:
                message +='\n'
                message += C_('Missing Dependency',
                              ' • <b>Polkit</b>'
                             )

        message += '\n\n'

        link = 'https://github.com/realmazharhussain/gdm-settings/wiki/Dependencies#how-to-install-dependencies'
        # Translators: Keep '<a href="{url}">' and '</a>' as is. The words between them will become
        # a link to '{url}' and '{url}' will be replaced by a real URL during program execution.
        message += _('Click <a href="{url}">here</a> for instructions on how '
                     'to install these dependencies on your system.'
                    ).format(url=link)

        dialog = Gtk.MessageDialog(
                         text = _('Missing Dependencies'),
                        modal = True,
                      buttons = Gtk.ButtonsType.OK,
                 message_type = Gtk.MessageType.ERROR,
                transient_for = self.window,
               secondary_text = message,
         secondary_use_markup = True,
        )

        dialog.connect('response', lambda *args: self.quit())
        dialog.present()


    def keyboard_shortcuts(self):
        self.set_accels_for_action("app.quit", ["<Ctrl>q"])
        self.set_accels_for_action("app.refresh", ["<Ctrl>r", "F5"])


    def create_actions(self):

        def create_action(action_name, function):
            action = Gio.SimpleAction(name=action_name)
            action.connect("activate", function)
            self.add_action(action)

        create_action("refresh", self.refresh_cb)
        create_action("import_user_settings", self.import_user_settings_cb)
        create_action("reset_settings", self.reset_settings_cb)
        create_action("about", self.about_cb)
        create_action("quit", self.quit_cb)


    def refresh_cb(self, action, user_data):
        self.settings_manager.drop_changes()

        toast = Adw.Toast(timeout=1, priority='high', title=_('Settings reloaded'))
        self.window.toast_overlay.add_toast(toast)


    def import_user_settings_cb(self, action, user_data):
        from .enums import PackageType
        if env.PACKAGE_TYPE is not PackageType.Flatpak:
            self.settings_manager.load_user_settings()
            toast = Adw.Toast(timeout=1, priority='high', title=_('User settings imported'))
            self.window.toast_overlay.add_toast(toast)
        else:
            toast = Adw.Toast(timeout=2, priority="high")
            toast.set_title(_("Importing user settings is NOT supported in Flatpak version"))
            self.window.toast_overlay.add_toast(toast)


    def reset_settings_cb(self, action, user_data):
        self.window.task_counter.inc()
        self.settings_manager.reset_settings_async(self.on_reset_settings_finish)

    def on_reset_settings_finish(self, settings_manager, result, nothing):
        success = settings_manager.reset_settings_finish(result)
        self.window.task_counter.dec()

        if success:
            message = _("Reset settings successfully")
        else:
            message = _("Failed to reset settings")

        toast = Adw.Toast(timeout=2, priority="high", title=message)
        self.window.toast_overlay.add_toast(toast)


    def about_cb(self, action, user_data):
        from .dialogs import AboutDialog
        dialog = AboutDialog(self.window)
        dialog.present()


    def quit_cb(self, action, user_data):
        self.quit()
