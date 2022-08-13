'''Contains the main Application class'''

import logging
from gettext import gettext as _, pgettext as C_

import gi
gi.require_version("Adw", '1')
from gi.repository import Adw, Gtk, Gio, GLib, Gdk

from . import env
from . import info

# Namespace to contain widgets
from types import SimpleNamespace
widgets = SimpleNamespace()

class Application(Adw.Application):
    '''The main Application class'''
    def __init__(self):
        Adw.Application.__init__(self, application_id=info.application_id)

        # Add command-line options

        from gi.repository.GLib import OptionFlags, OptionArg

        self.add_main_option('version', 0,                   # long name, short name (0 means no short name)
                             OptionFlags.NONE,               # OptionFlags
                             OptionArg.NONE,                 # OptionArg (type of argument required by this option)
                             C_('Description of --version option',
                                'Show application version'), # description of the option
                             None,                           # name of this option's argument
                             )

        self.add_main_option('verbosity', 0,
                             OptionFlags.NONE,
                             OptionArg.INT,
                             C_('Description of --verbosity option',
                                'Set verbosity level manually (from 0 to 5)'),
                             C_('Argument of --verbosity option',
                                'LEVEL'),
                             )

        self.add_main_option('verbose', ord('v'),
                             OptionFlags.NONE,
                             OptionArg.NONE,
                             C_('Description of --verbose option',
                                'Enable verbose mode (alias of --verbosity=5)'),
                             None,
                             )

        self.add_main_option('quiet', ord('q'),
                             OptionFlags.NONE,
                             OptionArg.NONE,
                             # Translators: Extra spaces here are to vertically align parentheses here with parentheses in description of option --verbose. Ignore them (or not).
                             C_('Description of --quiet option',
                                'Enable quiet mode   (alias of --verbosity=0)'),
                             None,
                             )

        # Connect signals
        self.connect("activate", self.on_activate)
        self.connect("handle-local-options", self.handle_local_options)
        self.connect("shutdown", self.on_shutdown)


    ## Core App Signal Handlers ##

    def on_activate(self, app):
        if win := self.get_active_window():
            win.present()
            return

        logging.info(f"Application Version    = {info.version}")
        logging.info(f"Operating System       = {env.OS_PRETTY_NAME}")
        logging.info(f"PackageType            = {env.PACKAGE_TYPE.name}")
        logging.info(f"TEMP_DIR               = {env.TEMP_DIR}")
        logging.info(f"HOST_DATA_DIRS         = {env.HOST_DATA_DIRS}")

        from .settings import SettingsManager
        self.settings_manager = SettingsManager()

        self.get_widgets()
        self.add_image_choosers()
        self.set_widget_properties()
        self.add_pages_to_page_stack()
        self.load_theme_lists()
        self.bind_to_gsettings()
        self.connect_signals()
        self.create_actions()
        self.keyboard_shortcuts()
        self.add_window(widgets.main_window)
        widgets.main_window.present()

        # Some dependencies cannot be packaged along with the app but are
        # required to be installed on the user's system. So, we need to
        # check them and report to the user if they are missing.
        self.check_system_dependencies()

    def handle_local_options(self, klass, options):

        if options.contains("version"):
            print (info.application_name, f"({info.project_name})", f"v{info.version}")
            return 0

        if options.contains("verbose"):
            self.set_logging_level (5)

        if options.contains("quiet"):
            self.set_logging_level (0)

        from gi.repository.GLib import VariantType
        if verbosity_gvariant := options.lookup_value("verbosity", VariantType("i")):
            verbosity_level = verbosity_gvariant.get_int32()

            if verbosity_level >= 0 and verbosity_level <= 5:
                self.set_logging_level (verbosity_level)
            else:
                from sys import stderr
                print(_('{level} is an invalid verbosity level. Accepted values are 0 to 5.').format(level=verbosity_level), file=stderr)
                print(_('Assuming Verbosity level 4.'), file=stderr)
                self.set_logging_level (4)

        return -1

    def on_shutdown(self, app):
        self.settings_manager.cleanup()


    ### Some utility functions ###

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

        gdm_installed = check_dependency('gdm') or check_dependency('gdm3')
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
                transient_for = widgets.main_window,
               secondary_text = message,
         secondary_use_markup = True,
        )

        dialog.connect('response', lambda *args: self.quit())
        dialog.present()

    def connect_signal(self, widget, signal, function):
        getattr(widgets, widget).connect(signal, function)

    def create_action(self, action_name, function):
        action = Gio.SimpleAction(name=action_name)
        action.connect("activate", function)
        self.add_action(action)
        setattr(widgets, action_name+'_action', action)

    def add_page_to_page_stack(self, title, name=None):
        name = name or title.lower().replace(" ", "_")
        page_content = getattr(widgets, name + '_page_content')
        page = widgets.page_stack.add_child(page_content)
        page.set_name(name)
        page.set_title(title)


    ### Signal handlers for Widgets ###

    def show_about_dialog(self):
        from .dialogs import AboutDialog
        dialog = AboutDialog(widgets.main_window)
        dialog.present()

    def show_app_preferences(self):
        import os

        file = os.path.join(info.data_dir, 'app-preferences.ui')
        builder = Gtk.Builder.new_from_file(file)
        pref_window = builder.get_object('app_preferences_window')
        pref_window.set_transient_for(widgets.main_window)
        pref_window.present()

    def on_apply(self, button):
        button.set_sensitive(False)
        widgets.spinner.set_spinning(True)
        self.settings_manager.apply_settings_async(self.on_apply_finished)

    def on_apply_finished(self, source_object, result, user_data):
        status = self.settings_manager.apply_settings_finish(result)

        if status.success:
            widgets.main_toast_overlay.add_toast(widgets.apply_succeeded_toast)
        else:
            widgets.main_toast_overlay.add_toast(widgets.apply_failed_toast)

        widgets.apply_button.set_sensitive(True)
        widgets.spinner.set_spinning(False)

    def on_apply_current_display_settings(self, button):

        try:
            status = self.settings_manager.apply_current_display_settings()
            toast = Adw.Toast(timeout=2, priority="high")
            if status.success:
                toast.props.title = _("Applied current display settings")
            else:
                toast.props.title = _("Failed to apply current display settings")
            widgets.main_toast_overlay.add_toast(toast)
        except FileNotFoundError:
            message = _(
                        "The file '$XDG_CONFIG_HOME/monitors.xml' is required to apply current"
                        " display settings but it does not exist.\n"
                        "\n"
                        "In order to create that file automatically,\n"
                        "\n"
                        "1. Go to 'Display' panel of System Settings.\n"
                        "2. Change some settings there.\n"
                        "3. Apply."
                       )

            dialog = Gtk.MessageDialog(
                             text = _('Monitor Settings Not Found'),
                            modal = True,
                          buttons = Gtk.ButtonsType.OK,
                     message_type = Gtk.MessageType.ERROR,
                    transient_for = widgets.main_window,
                   secondary_text = message,
             secondary_use_markup = True,
            )

            dialog.connect('response', lambda *args: dialog.close())
            dialog.present()

    def on_extract_shell_theme(self, button):
        from os.path import join
        from .gr_utils import extract_default_theme, ThemesDir

        perm_theme_name = 'default-extracted'
        perm_theme_path = join(ThemesDir, perm_theme_name)
        temp_theme_path = join(env.TEMP_DIR, 'extracted-theme')

        # Extract default shell theme to a temporary path
        extract_default_theme(temp_theme_path)

        # Appy top bar tweaks (if enabled)
        if widgets.include_top_bar_tweaks_switch.get_active():
            #self.set_settings()
            with open(join(temp_theme_path, 'gnome-shell', 'gnome-shell.css'), 'a') as shell_css:
                print(self.settings_manager.get_setting_css(), file=shell_css)

        # Copy extracted theme to its permanent path
        from .utils import CommandElevator
        command_elevator = CommandElevator()
        command_elevator.add(f'cp -rfT {temp_theme_path} {perm_theme_path}')
        status = command_elevator.run()

        # Notify the user via in-app notification
        toast = Adw.Toast(timeout=2, priority="high")
        if status:
            # Translators: Do not translate '{folder}' and '{name}'. Keep these as they are. They will be replaced by an actual folder path and theme name during runtime.
            toast.set_title(_("Default shell theme extracted to '{folder}' as '{name}'").format(folder=ThemesDir, name=perm_theme_name))
        else:
            toast.set_title(_("Failed to extract default theme"))
        widgets.main_toast_overlay.add_toast(toast)


    ### Other functions ###

    def set_logging_level(self, verbosity):
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


    def get_widgets(self):

        ui_files = [
            "main-window.ui",
            "appearance-page.ui",
            "fonts-page.ui",
            "display-page.ui",
            "sound-page.ui",
            "top-bar-page.ui",
            "pointing-page.ui",
            "misc-page.ui",
            "tools-page.ui",
        ]

        widget_list = [
            # Main Widgets
            "main_window",
            "paned",
            "app_menu",
            "page_stack",
            "appearance_page_content",
            "fonts_page_content",
            "display_page_content",
            "sound_page_content",
            "top_bar_page_content",
            "pointing_page_content",
            "misc_page_content",
            "tools_page_content",
            "spinner",
            "apply_button",
            "main_toast_overlay",
            "apply_failed_toast",
            "apply_succeeded_toast",
            "user_settings_imported_toast",
            "settings_reloaded_toast",

            # Widgets from Appearance page
            "shell_theme_comborow",
            "icon_theme_comborow",
            "cursor_theme_comborow",
            "background_type_comborow",
            "background_image_actionrow",
            #"background_image_button",
            #"background_image_chooser",
            "background_color_actionrow",
            "background_color_button",

            # Widgets from Fonts page
            "font_button",
            "antialiasing_comborow",
            "hinting_comborow",
            "scaling_factor_spinbutton",

            # Widgets from Top Bar page
            "disable_top_bar_arrows_switch",
            "disable_top_bar_rounded_corners_switch",
            "top_bar_text_color_switch",
            "top_bar_text_color_button",
            "top_bar_background_color_switch",
            "top_bar_background_color_button",
            "show_weekday_switch",
            "show_seconds_switch",
            "time_format_comborow",
            "show_battery_percentage_switch",

            # Widgets from Sound page
            "sound_theme_comborow",
            "event_sounds_switch",
            "feedback_sounds_switch",
            "over_amplification_switch",

            # Widgets from Mouse & Touchpad page
            "mouse_speed_scale",
            "pointer_acceleration_comborow",
            "mouse_inverse_scrolling_switch",
            "tap_to_click_switch",
            "natural_scrolling_switch",
            "two_finger_scrolling_switch",
            "disable_while_typing_switch",
            "touchpad_speed_scale",

            # Widgets from Display page
            "apply_current_display_settings_button",
            "night_light_enable_switch",
            "night_light_schedule_comborow",
            "night_light_start_box",
            "night_light_end_box",
            "night_light_start_hour_spinbutton",
            "night_light_start_minute_spinbutton",
            "night_light_end_hour_spinbutton",
            "night_light_end_minute_spinbutton",
            "night_light_color_temperature_scale",

            # Widgets from Misc page
            "enable_logo_switch",
            "logo_actionrow",
            #"logo_button",
            "enable_welcome_message_switch",
            "welcome_message_entry",
            "disable_restart_buttons_switch",
            "disable_user_list_switch",
            #"logo_chooser",

            # Widgets from Tools page
            "include_top_bar_tweaks_switch",
            "extract_shell_theme_button",
            #"extracted_theme_destination_chooser",
        ]



        # Initialize Builder
        self.builder = Gtk.Builder()
        self.builder.set_translation_domain(info.project_name)

        # Load UI files
        import os
        for ui_file_name in ui_files:
            file = os.path.join(info.data_dir, ui_file_name)
            self.builder.add_from_file(file)

        # Get Widgets from builder ####
        for widget in widget_list:
            setattr(widgets, widget, self.builder.get_object(widget))

    def add_image_choosers(self):
        from .common_widgets import ImageChooserButton

        widgets.background_image_button = ImageChooserButton(valign='center', hexpand=False)
        widgets.background_image_actionrow.add_suffix(widgets.background_image_button)
        widgets.background_image_actionrow.set_activatable_widget(widgets.background_image_button)

        widgets.logo_button = ImageChooserButton(valign='center', hexpand=False)
        widgets.logo_actionrow.add_suffix(widgets.logo_button)
        widgets.logo_actionrow.set_activatable_widget(widgets.logo_button)


    def bind_to_gsettings(self):
        from .bind_utils import bind, bind_colorbutton, bind_comborow
        from .bind_utils import bind_comborow_by_enum, bind_comborow_by_list

        #### Window State ####
        window_state_settings = Gio.Settings(schema_id=f'{info.application_id}.window-state')
        bind(window_state_settings, 'width', widgets.main_window, 'default-width')
        bind(window_state_settings, 'height', widgets.main_window, 'default-height')
        bind(window_state_settings, 'paned-position', widgets.paned, 'position')
        bind(window_state_settings, 'last-visited-page', widgets.page_stack, 'visible-child-name')

        #### Tools Page ####
        tools_settings = Gio.Settings(schema_id=f"{info.application_id}.tools")
        bind(tools_settings, 'top-bar-tweaks', widgets.include_top_bar_tweaks_switch, 'active')

        #### Appearance ####
        from .settings import appearance_settings
        from .enums import BackgroundType
        bind_comborow(widgets.shell_theme_comborow, appearance_settings, 'shell-theme')
        bind_comborow(widgets.icon_theme_comborow, appearance_settings, 'icon-theme')
        bind_comborow(widgets.cursor_theme_comborow, appearance_settings, 'cursor-theme')
        bind_comborow_by_enum(widgets.background_type_comborow,
                appearance_settings, 'background-type', BackgroundType)
        bind(appearance_settings, 'background-image', widgets.background_image_button, 'filename')
        bind_colorbutton(widgets.background_color_button, appearance_settings, 'background-color')

        #### Fonts ####
        from .settings import font_settings
        bind_comborow_by_list(widgets.antialiasing_comborow,
                font_settings, 'antialiasing', ['grayscale', 'rgba', 'none'])
        bind_comborow_by_list(widgets.hinting_comborow,
                font_settings, 'hinting', ['full', 'medium', 'slight', 'none'])
        bind(font_settings, 'scaling-factor', widgets.scaling_factor_spinbutton, 'value')
        bind(font_settings, 'font', widgets.font_button, 'font')

        #### Top Bar ####
        from .settings import top_bar_settings
        ## Tweaks ##
        bind(top_bar_settings, 'disable-arrows', widgets.disable_top_bar_arrows_switch, 'active')
        bind(top_bar_settings, 'disable-rounded-corners', widgets.disable_top_bar_rounded_corners_switch, 'active')
        bind(top_bar_settings, 'change-text-color', widgets.top_bar_text_color_switch, 'active')
        bind_colorbutton(widgets.top_bar_text_color_button, top_bar_settings, 'text-color')
        bind(top_bar_settings, 'change-background-color', widgets.top_bar_background_color_switch, 'active')
        bind_colorbutton(widgets.top_bar_background_color_button, top_bar_settings, 'background-color')
        ## Time/Clock ##
        bind(top_bar_settings, 'show-weekday', widgets.show_weekday_switch, 'active')
        bind(top_bar_settings, 'show-seconds', widgets.show_seconds_switch, 'active')
        bind_comborow_by_list(widgets.time_format_comborow, top_bar_settings, 'time-format', ['12h', '24h'])
        ## Power ##
        bind(top_bar_settings, 'show-battery-percentage', widgets.show_battery_percentage_switch, 'active')

        ##### Sound ####
        from .settings import sound_settings
        bind_comborow(widgets.sound_theme_comborow, sound_settings, 'theme')
        bind(sound_settings, 'event-sounds', widgets.event_sounds_switch, 'active')
        bind(sound_settings, 'feedback-sounds', widgets.feedback_sounds_switch, 'active')
        bind(sound_settings, 'over-amplification', widgets.over_amplification_switch, 'active')

        #### Mouse ####
        from .settings import mouse_settings
        bind_comborow_by_list(widgets.pointer_acceleration_comborow,
                mouse_settings, 'pointer-acceleration', ['default', 'flat', 'adaptive'])
        bind(mouse_settings, 'natural-scrolling', widgets.mouse_inverse_scrolling_switch, 'active')
        bind(mouse_settings, 'speed', widgets.mouse_speed_scale.props.adjustment, 'value')

        #### Touchpad ####
        from .settings import touchpad_settings
        bind(touchpad_settings, 'tap-to-click', widgets.tap_to_click_switch, 'active')
        bind(touchpad_settings, 'natural-scrolling', widgets.natural_scrolling_switch, 'active')
        bind(touchpad_settings, 'two-finger-scrolling', widgets.two_finger_scrolling_switch, 'active')
        bind(touchpad_settings, 'disable-while-typing', widgets.disable_while_typing_switch, 'active')
        bind(touchpad_settings, 'speed', widgets.touchpad_speed_scale.props.adjustment, 'value')

        #### Night Light ####
        from .settings import night_light_settings
        bind(night_light_settings, 'enabled', widgets.night_light_enable_switch, 'active')
        bind_comborow_by_list(widgets.night_light_schedule_comborow,
                night_light_settings, 'schedule-automatic', [True, False])
        bind(night_light_settings, 'start-hour', widgets.night_light_start_hour_spinbutton, 'value')
        bind(night_light_settings, 'start-minute', widgets.night_light_start_minute_spinbutton, 'value')
        bind(night_light_settings, 'end-hour', widgets.night_light_end_hour_spinbutton, 'value')
        bind(night_light_settings, 'end-minute', widgets.night_light_end_minute_spinbutton, 'value')
        bind(night_light_settings, 'temperature',
                widgets.night_light_color_temperature_scale.props.adjustment, 'value')

        #### Misc ####
        from .settings import misc_settings
        bind(misc_settings, 'disable-restart-buttons', widgets.disable_restart_buttons_switch, 'active')
        bind(misc_settings, 'disable-user-list', widgets.disable_user_list_switch, 'active')
        bind(misc_settings, 'enable-welcome-message', widgets.enable_welcome_message_switch, 'active')
        bind(misc_settings, 'welcome-message', widgets.welcome_message_entry, 'text')
        bind(misc_settings, 'enable-logo', widgets.enable_logo_switch, 'active')
        bind(misc_settings, 'logo', widgets.logo_button, 'filename')

    def set_widget_properties(self):
        # Main Window
        if info.build_type != 'release':
            widgets.main_window.add_css_class('devel')

        # Following properties are ignored when set in .ui files.
        # So, they need to be changed here.

        # Paned
        widgets.paned.set_shrink_start_child(False)
        widgets.paned.set_shrink_end_child(False)
        # Font Scaling Factor SpinButton
        widgets.scaling_factor_spinbutton.set_range(0.5, 3)
        widgets.scaling_factor_spinbutton.set_increments(0.1,0.5)
        # Mouse Speed Scale
        widgets.mouse_speed_scale.set_range(-1, 1)
        # Touchpad Speed Scale
        widgets.touchpad_speed_scale.set_range(-1, 1)
        # Night Light Start Box
        widgets.night_light_start_box.set_direction(Gtk.TextDirection.LTR)
        # Night Light End Box
        widgets.night_light_end_box.set_direction(Gtk.TextDirection.LTR)
        # Night Light Start Hour SpinButton
        widgets.night_light_start_hour_spinbutton.set_range(0, 23)
        widgets.night_light_start_hour_spinbutton.set_increments(1,2)
        # Night Light Start Minute SpinButton
        widgets.night_light_start_minute_spinbutton.set_range(0, 59)
        widgets.night_light_start_minute_spinbutton.set_increments(1,5)
        # Night Light End Hour SpinButton
        widgets.night_light_end_hour_spinbutton.set_range(0, 23)
        widgets.night_light_end_hour_spinbutton.set_increments(1,2)
        # Night Light End Minute SpinButton
        widgets.night_light_end_minute_spinbutton.set_range(0, 59)
        widgets.night_light_end_minute_spinbutton.set_increments(1,5)
        # Night Light Temperature Scale
        widgets.night_light_color_temperature_scale.set_range(1700, 4700)

    def load_theme_lists(self):
        # Shell Themes
        from .theme_lists import shell_themes
        widgets.shell_theme_list = Gtk.StringList()
        for theme_name in shell_themes.names:
            widgets.shell_theme_list.append(theme_name)
        widgets.shell_theme_comborow.set_model(widgets.shell_theme_list)

        # Icon Themes
        from .theme_lists import icon_themes
        widgets.icon_theme_list = Gtk.StringList()
        for theme_name in icon_themes.names:
            widgets.icon_theme_list.append(theme_name)
        widgets.icon_theme_comborow.set_model(widgets.icon_theme_list)

        # Cursor Themes
        from .theme_lists import cursor_themes
        widgets.cursor_theme_list = Gtk.StringList()
        for theme_name in cursor_themes.names:
            widgets.cursor_theme_list.append(theme_name)
        widgets.cursor_theme_comborow.set_model(widgets.cursor_theme_list)

        # Sound Themes
        from .theme_lists import sound_themes
        widgets.sound_theme_list = Gtk.StringList()
        for theme_name in sound_themes.names:
            widgets.sound_theme_list.append(theme_name)
        widgets.sound_theme_comborow.set_model(widgets.sound_theme_list)

    def connect_signals(self):
        self.connect_signal("apply_button", "clicked", self.on_apply)
        self.connect_signal("apply_current_display_settings_button", "clicked",
                            self.on_apply_current_display_settings)
        self.connect_signal("extract_shell_theme_button", "clicked", self.on_extract_shell_theme)

    def add_pages_to_page_stack(self):
        self.add_page_to_page_stack(_("Appearance"), 'appearance')
        self.add_page_to_page_stack(_("Fonts"), 'fonts')
        self.add_page_to_page_stack(_("Top Bar"), 'top_bar')
        self.add_page_to_page_stack(_("Sound"), 'sound')
        self.add_page_to_page_stack(_("Mouse & Touchpad"), 'pointing')
        self.add_page_to_page_stack(_("Display"), 'display')
        self.add_page_to_page_stack(_("Miscellaneous"), "misc")
        self.add_page_to_page_stack(_("Tools"), 'tools')

    def create_actions(self):
        self.create_action("quit", lambda x,y: self.quit())
        self.create_action("about", lambda x,y: self.show_about_dialog())
        self.create_action("preferences", lambda x,y: self.show_app_preferences())
        self.create_action("import_user_settings", lambda x,y: self.import_user_settings())
        self.create_action("refresh", lambda x,y: self.drop_changes())
        self.create_action("reset_settings", lambda x,y: self.reset_settings())

    def keyboard_shortcuts(self):
        self.set_accels_for_action("app.quit", ["<Ctrl>q"])
        self.set_accels_for_action("app.reload_settings", ["<Ctrl>r", "F5"])

    def drop_changes(self):
        self.settings_manager.drop_changes()
        widgets.main_toast_overlay.add_toast(widgets.settings_reloaded_toast)

    def import_user_settings(self):
        from .enums import PackageType
        if env.PACKAGE_TYPE is not PackageType.Flatpak:
            self.settings_manager.load_user_settings()
            widgets.main_toast_overlay.add_toast(widgets.user_settings_imported_toast)
        else:
            toast = Adw.Toast(timeout=2, priority="high")
            toast.set_title(_("Importing user settings is NOT supported in Flatpak version"))
            widgets.main_toast_overlay.add_toast(toast)

    def reset_settings(self):
        toast = Adw.Toast(timeout=2, priority="high",
                          title=_("Failed to reset settings"))

        if self.settings_manager.reset_settings():
            toast.set_title(_("Reset settings successfully"))

        widgets.main_toast_overlay.add_toast(toast)
