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
                                'Enable verbose mode (set verbosity level 5)'),
                             None,
                             )

        self.add_main_option('quiet', ord('q'),
                             OptionFlags.NONE,
                             OptionArg.NONE,
                             # Translators: Extra spaces here are to vertically align parentheses here with parentheses in description of option --verbose. Ignore them (or not).
                             C_('Description of --quiet option',
                                'Enable quiet mode   (set verbosity level 0)'),
                             None,
                             )

        # Connect signals
        self.connect("activate", self.on_activate)
        self.connect("handle-local-options", self.handle_local_options)
        self.connect("shutdown", self.on_shutdown)


    ## Core App Signal Handlers ##

    def on_activate(self, app):
        logging.info(f"Operating System       = {env.OS_PRETTY_NAME}")
        logging.info(f"PackageType            = {env.PACKAGE_TYPE.name}")

        self.initialize_settings()
        self.get_widgets()
        self.bind_to_gsettings()
        self.set_widget_properties()
        self.load_theme_lists()
        self.connect_signals()
        self.load_settings_to_widgets()
        self.add_pages_to_page_stack()
        self.create_actions()
        self.keyboard_shortcuts()
        self.restore_window_state()
        self.add_window(widgets.main_window)
        widgets.main_window.present()

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
        self.save_window_state()
        self.settings.cleanup()


    ### Some utility functions ###

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


    ### Settings getter functions ###

    def load_comborow_setting(self, name):
        comborow = getattr(widgets, name+'_comborow')
        setting  = getattr(self.settings, name)

        selection_position = 0;
        for item in comborow.get_model():
            if setting == item.get_string():
                comborow.set_selected(selection_position)
                break
            else:
                selection_position += 1


    ### Settings setter functions ###

    def set_file_chooser_setting(self, name):
        file_chooser = getattr(widgets, name+'_chooser')
        if file := file_chooser.get_file():
            setattr(self.settings, name, file.get_path())


    ### Signal handlers for Widgets ###

    def show_about_dialog(self):
        from .dialogs import AboutDialog
        dialog = AboutDialog(widgets.main_window)
        dialog.present()

    def show_app_preferences(self):
        from .utils import find_file
        file = find_file(f"{info.project_name}/app-preferences.ui", locations=env.XDG_DATA_DIRS)
        builder = Gtk.Builder.new_from_file(file)
        pref_window = builder.get_object('app_preferences_window')
        pref_window.set_transient_for(widgets.main_window)
        pref_window.present()

    def on_apply(self, widget):
        try:
            self.set_settings()

            # Apply
            if self.settings.apply_settings():
                widgets.main_toast_overlay.add_toast(widgets.apply_succeeded_toast)
            else:
                widgets.main_toast_overlay.add_toast(widgets.apply_failed_toast)

        except FileNotFoundError as e:
            toast = Adw.Toast (timeout=4, priority="high")
            toast.set_title (_("Didn't apply. Chosen background image could not be found. Please! choose again."))
            widgets.main_toast_overlay.add_toast (toast)

    def on_background_type_change(self, comborow, selection):
        selected = comborow.get_selected()
        if selected == 1:
            widgets.background_image_actionrow.show()
            widgets.background_color_actionrow.hide()
        elif selected == 2:
            widgets.background_color_actionrow.show()
            widgets.background_image_actionrow.hide()
        else:
            widgets.background_image_actionrow.hide()
            widgets.background_color_actionrow.hide()

    def on_background_image_chooser_response(self, widget, response):
        if response == Gtk.ResponseType.ACCEPT:
          image_file = widgets.background_image_chooser.get_file()
          image_basename = image_file.get_basename()
          widgets.background_image_button.set_label(image_basename)
        widgets.background_image_chooser.hide()

    def on_logo_chooser_response(self, widget, response):
        if response == Gtk.ResponseType.ACCEPT:
          image_file = widgets.logo_chooser.get_file()
          image_basename = image_file.get_basename()
          widgets.logo_button.set_label(image_basename)
        widgets.logo_chooser.hide()

    def on_apply_current_display_settings(self, button):
        toast = Adw.Toast(timeout=2, priority="high")
        if self.settings.apply_current_display_settings():
            toast.set_title(_("Applied current display settings"))
        else:
            toast.set_title(_("Failed to apply current display settings"))
        widgets.main_toast_overlay.add_toast(toast)

    def on_extract_shell_theme(self, button):
        from os.path import join
        temp_theme_path = join(env.TEMP_DIR, 'extracted-theme')
        perm_theme_dir  = env.SYSTEM_DATA_DIRS[0]
        perm_theme_name = 'default-extracted'
        perm_theme_path = join(perm_theme_dir, perm_theme_name)

        # Extract default shell theme to a temporary path
        self.settings.gresource_utils.extract_default_shell_theme(temp_theme_path)

        # Appy top bar tweaks (if enabled)
        if widgets.include_top_bar_tweaks_switch.get_active():
            self.set_settings()
            with open(join(temp_theme_path, 'gnome-shell', 'gnome-shell.css'), 'a') as shell_css:
                print(self.settings.get_setting_css(), file=shell_css)

        # Copy extracted theme to its permanent path
        from .utils import CommandElevator
        command_elevator = CommandElevator()
        command_elevator.add(f'cp -rfT {temp_theme_path} {perm_theme_path}')
        status = command_elevator.run()

        # Notify the user via in-app notification
        toast = Adw.Toast(timeout=2, priority="high")
        if status:
            # Translators: Do not translate '{folder}' and '{name}'. Keep these as they are. They will be replaced by an actual folder path and theme name during runtime.
            toast.set_title(_("Default shell theme extracted to '{folder}' as '{name}'").format(folder=perm_theme_dir, name=perm_theme_name))
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

    def initialize_settings(self):
        from .settings import Settings
        self.settings = Settings()
        self.window_state = Gio.Settings(schema_id=f'{info.application_id}.window-state')

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
            "background_image_button",
            "background_image_chooser",
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
            "logo_button",
            "enable_welcome_message_switch",
            "welcome_message_entry",
            "disable_restart_buttons_switch",
            "disable_user_list_switch",
            "logo_chooser",

            # Widgets from Tools page
            "include_top_bar_tweaks_switch",
            "extract_shell_theme_button",
            #"extracted_theme_destination_chooser",
        ]

        # Initialize Builder
        self.builder = Gtk.Builder()
        self.builder.set_translation_domain(info.project_name)

        # Load UI files
        from .utils import find_file
        for ui_file_name in ui_files:
            file = find_file(f"{info.project_name}/{ui_file_name}", locations=env.XDG_DATA_DIRS)
            self.builder.add_from_file(file)

        # Get Widgets from builder ####
        for widget in widget_list:
            setattr(widgets, widget, self.builder.get_object(widget))

    def bind_to_gsettings(self):
        tools_gsettings = Gio.Settings(schema_id=f"{info.application_id}.tools")
        tools_gsettings.bind('top-bar-tweaks', widgets.include_top_bar_tweaks_switch, 'active', Gio.SettingsBindFlags.DEFAULT)

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
        for theme in shell_themes:
            widgets.shell_theme_list.append(theme.name)
        widgets.shell_theme_comborow.set_model(widgets.shell_theme_list)

        # Icon Themes
        from .theme_lists import icon_themes
        widgets.icon_theme_list = Gtk.StringList()
        for theme in icon_themes:
            widgets.icon_theme_list.append(theme.name)
        widgets.icon_theme_comborow.set_model(widgets.icon_theme_list)

        # Cursor Themes
        from .theme_lists import cursor_themes
        widgets.cursor_theme_list = Gtk.StringList()
        for theme in cursor_themes:
            widgets.cursor_theme_list.append(theme.name)
        widgets.cursor_theme_comborow.set_model(widgets.cursor_theme_list)

        # Sound Themes
        from .theme_lists import sound_themes
        widgets.sound_theme_list = Gtk.StringList()
        for theme in sound_themes:
            widgets.sound_theme_list.append(theme.name)
        widgets.sound_theme_comborow.set_model(widgets.sound_theme_list)

    def connect_signals(self):
        self.connect_signal("apply_button", "clicked", self.on_apply)
        self.connect_signal("background_type_comborow", "notify::selected", self.on_background_type_change)
        self.connect_signal("background_image_button", "clicked",
                            lambda x: widgets.background_image_chooser.show(),
                           )
        self.connect_signal("background_image_chooser", "response", self.on_background_image_chooser_response)
        self.connect_signal("logo_button", "clicked", lambda x: widgets.logo_chooser.show())
        self.connect_signal("logo_chooser", "response", self.on_logo_chooser_response)

        self.connect_signal("apply_current_display_settings_button", "clicked",
                            self.on_apply_current_display_settings)
        self.connect_signal("extract_shell_theme_button", "clicked", self.on_extract_shell_theme)

    def load_settings_to_widgets(self):
        #### Appearance ####
        # Themes
        self.load_comborow_setting('shell_theme')
        self.load_comborow_setting('icon_theme')
        self.load_comborow_setting('cursor_theme')

        # Background Type
        from .enums import BackgroundType
        widgets.background_type_comborow.set_selected(BackgroundType[self.settings.background_type].value)

        # Background Color
        background_color_rgba = Gdk.RGBA()
        background_color_rgba.parse(self.settings.background_color)
        widgets.background_color_button.set_rgba(background_color_rgba)

        # Background Image
        from os import path
        if self.settings.background_image:
            widgets.background_image_button.set_label(path.basename(self.settings.background_image))
            widgets.background_image_chooser.set_file(Gio.File.new_for_path(self.settings.background_image))

        #### Fonts ####
        from .enums import AntiAliasing, FontHinting
        widgets.antialiasing_comborow.set_selected(AntiAliasing[self.settings.antialiasing].value)
        widgets.hinting_comborow.set_selected(FontHinting[self.settings.hinting].value)
        widgets.scaling_factor_spinbutton.set_value(self.settings.scaling_factor)
        widgets.font_button.set_font(self.settings.font)

        #### Top Bar ####
        ## Tweaks ##
        # Arrows
        widgets.disable_top_bar_arrows_switch.set_active(self.settings.disable_top_bar_arrows)
        # Rounded Corners
        widgets.disable_top_bar_rounded_corners_switch.set_active(self.settings.disable_top_bar_rounded_corners)
        # Text Color
        widgets.top_bar_text_color_switch.set_active(self.settings.change_top_bar_text_color)
        top_bar_text_color_rgba = Gdk.RGBA()
        top_bar_text_color_rgba.parse(self.settings.top_bar_text_color)
        widgets.top_bar_text_color_button.set_rgba(top_bar_text_color_rgba)
        # Background Color
        widgets.top_bar_background_color_switch.set_active(self.settings.change_top_bar_background_color)
        top_bar_background_color_rgba = Gdk.RGBA()
        top_bar_background_color_rgba.parse(self.settings.top_bar_background_color)
        widgets.top_bar_background_color_button.set_rgba(top_bar_background_color_rgba)
        ## Time/Clock ##
        widgets.show_weekday_switch.set_active(self.settings.show_weekday)
        widgets.show_seconds_switch.set_active(self.settings.show_seconds)
        widgets.time_format_comborow.set_selected(0 if self.settings.time_format == "12h" else 1)
        ## Power ##
        widgets.show_battery_percentage_switch.set_active(self.settings.show_battery_percentage)

        ##### Sound ####
        # Theme
        self.load_comborow_setting('sound_theme')
        widgets.event_sounds_switch.set_active(self.settings.event_sounds)
        widgets.feedback_sounds_switch.set_active(self.settings.feedback_sounds)
        widgets.over_amplification_switch.set_active(self.settings.over_amplification)

        #### Pointing ####
        ## Mouse ##
        from .enums import MouseAcceleration
        widgets.pointer_acceleration_comborow.set_selected(MouseAcceleration[self.settings.pointer_acceleration].value)
        widgets.mouse_inverse_scrolling_switch.set_active(self.settings.inverse_scrolling)
        widgets.mouse_speed_scale.set_value(self.settings.mouse_speed)
        ## Touchpad ##
        widgets.tap_to_click_switch.set_active(self.settings.tap_to_click)
        widgets.natural_scrolling_switch.set_active(self.settings.natural_scrolling)
        widgets.two_finger_scrolling_switch.set_active(self.settings.two_finger_scrolling)
        widgets.disable_while_typing_switch.set_active(self.settings.disable_while_typing)
        widgets.touchpad_speed_scale.set_value(self.settings.touchpad_speed)

        #### Night Light ####
        widgets.night_light_enable_switch.set_active(self.settings.night_light_enabled)

        if self.settings.night_light_schedule_automatic:
            widgets.night_light_schedule_comborow.set_selected(0)
        else:
            widgets.night_light_schedule_comborow.set_selected(1)

        widgets.night_light_start_hour_spinbutton.set_value(self.settings.night_light_start_hour)
        widgets.night_light_start_minute_spinbutton.set_value(self.settings.night_light_start_minute)
        widgets.night_light_end_hour_spinbutton.set_value(self.settings.night_light_end_hour)
        widgets.night_light_end_minute_spinbutton.set_value(self.settings.night_light_end_minute)
        widgets.night_light_color_temperature_scale.set_value(self.settings.night_light_temperature)

        #### Misc ####
        widgets.disable_restart_buttons_switch.set_active(self.settings.disable_restart_buttons)
        widgets.disable_user_list_switch.set_active(self.settings.disable_user_list)
        widgets.enable_welcome_message_switch.set_active(self.settings.enable_welcome_message)
        widgets.welcome_message_entry.set_text(self.settings.welcome_message)
        widgets.enable_logo_switch.set_active(self.settings.enable_logo)
        if self.settings.logo:
            from os import path
            widgets.logo_button.set_label(path.basename(self.settings.logo))
            widgets.logo_chooser.set_file(Gio.File.new_for_path(self.settings.logo))

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
        self.create_action("reload_settings", lambda x,y: self.reload_settings_to_widgets())
        self.create_action("reset_settings", lambda x,y: self.reset_settings())

    def keyboard_shortcuts(self):
        self.set_accels_for_action("app.quit", ["<Ctrl>q"])
        self.set_accels_for_action("app.reload_settings", ["<Ctrl>r", "F5"])

    def restore_window_state(self):
        # Window Size
        width = self.window_state.get_uint("width")
        height = self.window_state.get_uint("height")
        widgets.main_window.set_default_size(width, height)

        # Paned Position
        paned_position = self.window_state.get_uint("paned-position")
        widgets.paned.set_position(paned_position)

        # Last visited Page
        page_name = self.window_state.get_string("last-visited-page")
        widgets.page_stack.set_visible_child_name(page_name)

    def save_window_state(self):
        # Window Size
        width, height = widgets.main_window.get_default_size()
        self.window_state.set_uint("width", width)
        self.window_state.set_uint("height", height)

        # Paned Position
        paned_position = widgets.paned.get_position()
        self.window_state.set_uint("paned-position", paned_position)

        # Last visited Page
        page_name = widgets.page_stack.get_visible_child_name()
        self.window_state.set_string("last-visited-page", page_name)

    def reload_settings_to_widgets(self):
        self.settings.load_settings()
        self.load_settings_to_widgets()
        widgets.main_toast_overlay.add_toast(widgets.settings_reloaded_toast)

    def import_user_settings(self):
        from .enums import PackageType
        if env.PACKAGE_TYPE is not PackageType.Flatpak:
            self.settings.load_user_settings()
            self.load_settings_to_widgets()
            widgets.main_toast_overlay.add_toast(widgets.user_settings_imported_toast)
        else:
            toast = Adw.Toast(timeout=2, priority="high")
            toast.set_title(_("Importing user settings is NOT supported in Flatpak version"))
            widgets.main_toast_overlay.add_toast(toast)

    def reset_settings(self):
        toast = Adw.Toast(timeout=2, priority="high",
                          title=_("Failed to reset settings"))

        if self.settings.reset_settings():
            self.load_settings_to_widgets()
            toast.set_title(_("Reset settings successfully"))

        widgets.main_toast_overlay.add_toast(toast)

    def set_settings(self):
        ## Appearance ##
        # Themes
        self.settings.shell_theme  = widgets.shell_theme_comborow.get_selected_item().get_string()
        self.settings.icon_theme   = widgets.icon_theme_comborow.get_selected_item().get_string()
        self.settings.cursor_theme = widgets.cursor_theme_comborow.get_selected_item().get_string()
        # Background
        from .enums import BackgroundType
        self.settings.background_type  = BackgroundType(widgets.background_type_comborow.get_selected()).name
        self.settings.background_color = widgets.background_color_button.get_rgba().to_string()
        self.set_file_chooser_setting("background_image")

        ## Fonts ##
        from .enums import AntiAliasing, FontHinting
        self.settings.hinting = FontHinting(widgets.hinting_comborow.get_selected()).name
        self.settings.antialiasing = AntiAliasing(widgets.antialiasing_comborow.get_selected()).name
        self.settings.scaling_factor = widgets.scaling_factor_spinbutton.get_value()
        self.settings.font = widgets.font_button.get_font()

        ## Tob Bar ##
        # Tweaks
        self.settings.top_bar_text_color = widgets.top_bar_text_color_button.get_rgba().to_string()
        self.settings.disable_top_bar_arrows    = widgets.disable_top_bar_arrows_switch.get_active()
        self.settings.top_bar_background_color  = widgets.top_bar_background_color_button.get_rgba().to_string()
        self.settings.change_top_bar_text_color = widgets.top_bar_text_color_switch.get_active()
        self.settings.change_top_bar_background_color = widgets.top_bar_background_color_switch.get_active()
        self.settings.disable_top_bar_rounded_corners = widgets.disable_top_bar_rounded_corners_switch.get_active()
        # Time/Clock
        self.settings.show_weekday = widgets.show_weekday_switch.get_active()
        self.settings.show_seconds = widgets.show_seconds_switch.get_active()
        self.settings.time_format  = "12h" if widgets.time_format_comborow.get_selected() == 0 else '24h'
        # Power
        self.settings.show_battery_percentage  = widgets.show_battery_percentage_switch.get_active()

        ## Sound ##
        self.settings.sound_theme = widgets.sound_theme_comborow.get_selected_item().get_string()
        self.settings.feedback_sounds = widgets.feedback_sounds_switch.get_active()
        self.settings.over_amplification = widgets.over_amplification_switch.get_active()

        ## Pointing ##
        # Mouse
        from .enums import MouseAcceleration
        self.settings.pointer_acceleration = MouseAcceleration(widgets.pointer_acceleration_comborow.get_selected()).name
        self.settings.mouse_speed = widgets.mouse_speed_scale.get_value()
        self.settings.inverse_scrolling   = widgets.mouse_inverse_scrolling_switch.get_active()
        # Touchpad
        self.settings.tap_to_click = widgets.tap_to_click_switch.get_active()
        self.settings.touchpad_speed = widgets.touchpad_speed_scale.get_value()
        self.settings.natural_scrolling = widgets.natural_scrolling_switch.get_active()
        self.settings.two_finger_scrolling = widgets.two_finger_scrolling_switch.get_active()
        self.settings.disable_while_typing = widgets.disable_while_typing_switch.get_active()

        ## Night Light ##
        self.settings.night_light_enabled      = widgets.night_light_enable_switch.get_active()
        self.settings.night_light_temperature  = widgets.night_light_color_temperature_scale.get_value()
        self.settings.night_light_start_hour   = widgets.night_light_start_hour_spinbutton.get_value()
        self.settings.night_light_start_minute = widgets.night_light_start_minute_spinbutton.get_value()
        self.settings.night_light_end_hour     = widgets.night_light_end_hour_spinbutton.get_value()
        self.settings.night_light_end_minute   = widgets.night_light_end_minute_spinbutton.get_value()

        self.settings.night_light_schedule_automatic = False
        if widgets.night_light_schedule_comborow.get_selected() == 0:
            self.settings.night_light_schedule_automatic = True

        #### Misc ####
        self.settings.disable_restart_buttons = widgets.disable_restart_buttons_switch.get_active()
        self.settings.disable_user_list = widgets.disable_user_list_switch.get_active()
        self.settings.enable_logo = widgets.enable_logo_switch.get_active()
        self.set_file_chooser_setting("logo")
        self.settings.enable_welcome_message = widgets.enable_welcome_message_switch.get_active()
        self.settings.welcome_message = widgets.welcome_message_entry.get_text()
