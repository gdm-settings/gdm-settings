'''Contains the actual settings manager'''

import logging
from os import path
from gettext import gettext as _, pgettext as C_
from .enums import PackageType
from .utils import CommandElevator
from . import env

class GResourceUtils:
    ''' Utilities (functions) for 'gnome-shell-theme.gresource' file '''

    def __init__(self, command_elevator:CommandElevator=None):
        self.command_elevator         = command_elevator or CommandElevator()
        self.CustomThemeIdentity      = 'custom-theme'
        self.ThemesDir                = path.join(env.SYSTEM_DATA_DIRS[0], 'themes')
        self.GdmUsername              = 'gdm'
        self.ShellGresourceFile       = None
        self.ShellGresourceAutoBackup = None
        self.CustomGresourceFile      = None
        self.UbuntuGdmGresourceFile   = None

        for data_dir in env.SYSTEM_DATA_DIRS:
            file = path.join (data_dir,  'gnome-shell', 'gnome-shell-theme.gresource')
            if path.isfile (env.HOST_ROOT + file):
                self.ShellGresourceFile       = file
                self.ShellGresourceAutoBackup = self.ShellGresourceFile + ".default"
                self.CustomGresourceFile      = self.ShellGresourceFile + ".gdm_settings"
                break

        if 'ubuntu' in [env.OS_ID] + env.OS_ID_LIKE.split():
            from packaging.version import Version
            if Version(env.OS_VERSION_ID) >= Version('21.10'):
                self.UbuntuGdmGresourceFile = '/usr/share/gnome-shell/gdm-theme.gresource'
            else:
                self.UbuntuGdmGresourceFile = '/usr/share/gnome-shell/gdm3-theme.gresource'
        elif 'debian' in [env.OS_ID] + env.OS_ID_LIKE.split():
            self.GdmUsername = 'Debian-gdm'

        logging.info(f"ShellGresourceFile     = {self.ShellGresourceFile}")
        logging.info(f"UbuntuGdmGresourceFile = {self.UbuntuGdmGresourceFile}")

    def is_default(self, gresourceFile:str):
        """checks if the provided file is a GResource file of the default theme"""

        from .utils import getstdout

        if path.exists(gresourceFile):
            if getstdout(["gresource", "list", gresourceFile, "/org/gnome/shell/theme/gnome-shell.css"]):
                if not getstdout(f"gresource list {gresourceFile} /org/gnome/shell/theme/{self.CustomThemeIdentity}"):
                    return True
        return False

    def get_default(self) -> str:
        """get full path to the GResource file of the default theme (if the file exists)"""

        for file in self.ShellGresourceFile, self.ShellGresourceAutoBackup:
           if self.is_default(env.HOST_ROOT + file):
               return file

    def extract_default_shell_theme(self, destination:str, /):
        from os import makedirs
        from .utils import getstdout

        if path.exists(destination):
            from shutil import rmtree
            rmtree(destination)

        destination_shell_dir = path.join(destination, 'gnome-shell')
        gresource_file = self.get_default()
        resource_list = getstdout(["gresource", "list", gresource_file]).decode().splitlines()

        if not gresource_file:
            raise FileNotFoundError('No unmodified GResource file of the default shell theme was found')

        for resource in resource_list:
            filename = resource.removeprefix("/org/gnome/shell/theme/")
            filepath = path.join(destination_shell_dir, filename)
            content  = getstdout(["gresource", "extract", env.HOST_ROOT + gresource_file, resource])

            makedirs(path.dirname(filepath), exist_ok=True)

            with open(filepath, "wb") as opened_file:
                opened_file.write(content)

    def compile(self, shellDir:str, additional_css:str, background_image:str=''):
        """Compile a theme into a GResource file for its use as a GDM theme"""

        from os import remove
        from shutil import copy, copytree, rmtree

        temp_gresource_file = path.join(env.TEMP_DIR, 'gnome-shell-theme.gresource')
        temp_theme_dir = path.join(env.TEMP_DIR, 'extracted-theme')
        temp_shell_dir = path.join(temp_theme_dir, 'gnome-shell')

        # Remove temporary directory if already exists
        if path.exists(temp_theme_dir):
            rmtree(temp_theme_dir)

        # Remove temporary file if already exists
        if path.exists(temp_gresource_file):
            remove(temp_gresource_file)

        # Copy default resources to temporary directory
        self.extract_default_shell_theme(temp_theme_dir)

        # Copy gnome-shell dir of theme to temporary directory
        if shellDir:
            copytree(shellDir, temp_shell_dir, dirs_exist_ok=True)

        # Inject custom-theme identity
        open(path.join(temp_shell_dir, self.CustomThemeIdentity), 'w').close()

        # Background Image
        if background_image:
            copy(background_image, path.join(temp_shell_dir, 'background'))

        # Additional CSS
        with open(f"{temp_shell_dir}/gnome-shell.css", "a") as shell_css:
            print(additional_css, file=shell_css)

        # Copy gnome-shell.css to gdm.css and gdm3.css
        copy(f"{temp_shell_dir}/gnome-shell.css", f"{temp_shell_dir}/gdm.css")
        copy(f"{temp_shell_dir}/gnome-shell.css", f"{temp_shell_dir}/gdm3.css")

        # Get a list of all files in the shell theme
        # Note: We do this before calling open() so as not to include .gresource.xml file itself in the list
        from .utils import listdir_recursive
        file_list = listdir_recursive(temp_shell_dir)

        gresource_xml_filename = path.join(temp_shell_dir, 'gnome-shell-theme.gresource.xml')

        # Create gnome-shell-theme.gresource.xml file
        with open(gresource_xml_filename, 'w') as GresourceXml:
            print('<?xml version="1.0" encoding="UTF-8"?>',
                  '<gresources>',
                  ' <gresource prefix="/org/gnome/shell/theme">',
                *('  <file>'+file+'</file>' for file in file_list),
                  ' </gresource>',
                  '</gresources>',

                  sep='\n',
                  file=GresourceXml,
                 )

        # Compile Theme
        from subprocess import run
        run(['glib-compile-resources',
             '--sourcedir', temp_shell_dir,
             '--target', temp_gresource_file,
             gresource_xml_filename,
           ])

        # Return path to the generated GResource file
        return  temp_gresource_file

class Settings:
    key = "key"
    section = "section"
    key_type = "key_type"

    __key_list = [
        ## Appearance ##
        {section:"appearance", key_type:"string", key:"shell-theme"},
        {section:"appearance", key_type:"string", key:'icon-theme'},
        {section:"appearance", key_type:"string", key:'cursor-theme'},
        {section:"appearance", key_type:"string", key:"background-type"},
        {section:"appearance", key_type:"string", key:"background-image"},
        {section:"appearance", key_type:"string", key:"background-color"},
        ## Fonts ##
        {section:"fonts", key_type:"string", key:"font"},
        {section:"fonts", key_type:"string", key:"antialiasing"},
        {section:"fonts", key_type:"string", key:"hinting"},
        {section:"fonts", key_type:"double", key:"scaling-factor"},

        ## Top Bar ##
        # Tweaks
        {section:"top-bar", key_type:"boolean", key:"disable-top-bar-arrows"},
        {section:"top-bar", key_type:"boolean", key:"disable-top-bar-rounded-corners"},
        {section:"top-bar", key_type:"boolean", key:"change-top-bar-text-color"},
        {section:"top-bar", key_type:"string",  key:"top-bar-text-color"},
        {section:"top-bar", key_type:"boolean", key:"change-top-bar-background-color"},
        {section:"top-bar", key_type:"string",  key:"top-bar-background-color"},
        # Time/Clock
        {section:"top-bar", key_type:"boolean", key:'show-weekday'},
        {section:"top-bar", key_type:"string",  key:'time-format'},
        {section:"top-bar", key_type:"boolean", key:'show-seconds'},
        # Power
        {section:"top-bar", key_type:"boolean", key:'show-battery-percentage'},

        ## Sound ##
        {section:"sound", key_type:"string",  key:'sound-theme'},
        {section:"sound", key_type:"boolean", key:'event-sounds'},
        {section:"sound", key_type:"boolean", key:'feedback-sounds'},
        {section:"sound", key_type:"boolean", key:'over-amplification'},

        ## Pointing ##
        # Mouse
        {section:"mouse", key_type:"string",  key:'pointer-acceleration'},
        {section:"mouse", key_type:"boolean", key:'inverse-scrolling'},
        {section:"mouse", key_type:"double",  key:'mouse-speed'},
        # Touchpad
        {section:"touchpad", key_type:"boolean", key:'tap-to-click'},
        {section:"touchpad", key_type:"boolean", key:'natural-scrolling'},
        {section:"touchpad", key_type:"boolean", key:'two-finger-scrolling'},
        {section:"touchpad", key_type:"boolean", key:'disable-while-typing'},
        {section:"touchpad", key_type:"double",  key:'touchpad-speed'},

        ## Night Light ##
        {section:"night-light", key_type:"boolean", key:'night-light-enabled'},
        {section:"night-light", key_type:"boolean", key:'night-light-schedule-automatic'},
        {section:"night-light", key_type:"uint",    key:'night-light-temperature'},
        {section:"night-light", key_type:"int",     key:'night-light-start-hour'},
        {section:"night-light", key_type:"int",     key:'night-light-start-minute'},
        {section:"night-light", key_type:"int",     key:'night-light-end-hour'},
        {section:"night-light", key_type:"int",     key:'night-light-end-minute'},

        ## Misc ##
        {section:"misc", key_type:"boolean", key:"enable-welcome-message"},
        {section:"misc", key_type:"string",  key:"welcome-message"},
        {section:"misc", key_type:"boolean", key:"enable-logo"},
        {section:"misc", key_type:"string",  key:"logo"},
        {section:"misc", key_type:"boolean", key:"disable-restart-buttons"},
        {section:"misc", key_type:"boolean", key:"disable-user-list"},
    ]

    def __init__(self):
        logging.info(f"TEMP_DIR               = {env.TEMP_DIR}")
        logging.info(f"SYSTEM_DATA_DIRS       = {env.SYSTEM_DATA_DIRS}")

        self.gresource_utils  = GResourceUtils()
        self.command_elevator = self.gresource_utils.command_elevator

        from gi.repository import Gio
        from .info import application_id
        gsettings = lambda x=None: Gio.Settings (schema_id=application_id+('.'+x if x else ''))

        self.main_gsettings        = gsettings ()
        self.appearance_gsettings  = gsettings ('appearance')
        self.fonts_gsettings       = gsettings ('fonts')
        self.top_bar_gsettings     = gsettings ('top-bar')
        self.sound_gsettings       = gsettings ('sound')
        self.pointing_gsettings    = gsettings ('pointing')
        self.mouse_gsettings       = gsettings ('pointing.mouse')
        self.touchpad_gsettings    = gsettings ('pointing.touchpad')
        self.night_light_gsettings = gsettings ('night-light')
        self.misc_gsettings        = gsettings ('misc')

        self.load_settings()

    def load_settings(self):
        ''' Load settings '''

        self.load_from_gsettings()

        if self.main_gsettings.get_boolean("never-applied") \
        and env.PACKAGE_TYPE is not PackageType.Flatpak:
            self.load_user_settings()

    def _settings(self, schema_id:str):
        from gi.repository import Gio
        if schema := Gio.SettingsSchemaSource.get_default().lookup(schema_id, recursive=True):
            return Gio.Settings(schema_id=schema_id)


    def load_user_settings(self):
        ''' Load settings from user's session '''


        if user_theme_settings := self._settings('org.gnome.shell.extensions.user-theme'):
            self.shell_theme = user_theme_settings.get_string('name') or 'default'

        # Appearance
        if interface_settings := self._settings("org.gnome.desktop.interface"):
            self.icon_theme = interface_settings.get_string("icon-theme")
            self.cursor_theme = interface_settings.get_string("cursor-theme")

            self.font = interface_settings.get_string("font-name")
            self.antialiasing = interface_settings.get_string("font-antialiasing")
            self.hinting = interface_settings.get_string("font-hinting")
            self.scaling_factor = interface_settings.get_double("text-scaling-factor")

            self.show_weekday = interface_settings.get_boolean("clock-show-weekday")
            self.time_format = interface_settings.get_string("clock-format")
            self.show_seconds = interface_settings.get_boolean("clock-show-seconds")
            self.show_battery_percentage = interface_settings.get_boolean("show-battery-percentage")

        if sound_settings := self._settings("org.gnome.desktop.sound"):
            self.sound_theme = sound_settings.get_string("theme-name")
            self.event_sounds = sound_settings.get_boolean("event-sounds")
            self.feedback_sounds = sound_settings.get_boolean("input-feedback-sounds")
            self.over_amplification = sound_settings.get_boolean("allow-volume-above-100-percent")

        if mouse_settings := self._settings("org.gnome.desktop.peripherals.mouse"):
            self.pointer_acceleration = mouse_settings.get_string("accel-profile")
            self.inverse_scrolling = mouse_settings.get_boolean("natural-scroll")
            self.mouse_speed = mouse_settings.get_double("speed")

        if touchpad_settings := self._settings("org.gnome.desktop.peripherals.touchpad"):
            self.tap_to_click = touchpad_settings.get_boolean("tap-to-click")
            self.natural_scrolling = touchpad_settings.get_boolean("natural-scroll")
            self.two_finger_scrolling = touchpad_settings.get_boolean("two-finger-scrolling-enabled")
            self.disable_while_typing = touchpad_settings.get_boolean("disable-while-typing")
            self.touchpad_speed = touchpad_settings.get_double("speed")

        if night_light_settings := self._settings("org.gnome.settings-daemon.plugins.color"):
            self.night_light_enabled = night_light_settings.get_boolean("night-light-enabled")
            self.night_light_schedule_automatic = night_light_settings.get_boolean("night-light-schedule-automatic")
            self.night_light_temperature = night_light_settings.get_uint("night-light-temperature")

            night_light_schedule_from = night_light_settings.get_double("night-light-schedule-from")
            night_light_schedule_to = night_light_settings.get_double("night-light-schedule-to")

            from math import trunc

            self.night_light_start_hour = trunc(night_light_schedule_from)
            self.night_light_start_minute = round( (night_light_schedule_from % 1) * 60 )
            if self.night_light_start_minute == 60:
                self.night_light_start_hour += 1
                self.night_light_start_minute = 0

            self.night_light_end_hour = trunc(night_light_schedule_to)
            self.night_light_end_minute = round( (night_light_schedule_to % 1) * 60 )
            if self.night_light_end_minute == 60:
                self.night_light_end_hour += 1
                self.night_light_end_minute = 0

        if login_screen_settings := self._settings("org.gnome.login-screen"):
            self.enable_welcome_message = login_screen_settings.get_boolean("banner-message-enable")
            self.welcome_message = login_screen_settings.get_string("banner-message-text")
            self.logo = login_screen_settings.get_string("logo")
            self.enable_logo = bool(self.logo)
            self.disable_restart_buttons = login_screen_settings.get_boolean("disable-restart-buttons")
            self.disable_user_list = login_screen_settings.get_boolean("disable-user-list")

    def __load_value(self, section, key, key_type):
        gsettings = getattr(self, section.replace('-','_') + '_gsettings')
        get_value = getattr(gsettings, 'get_' + key_type)
        setattr(self, key.replace('-','_'), get_value(key))

    def __save_value(self, section, key, key_type):
        gsettings = getattr(self, section.replace('-','_') + '_gsettings')
        set_value = getattr(gsettings, 'set_' + key_type)
        set_value(key, getattr(self, key.replace('-','_')))

    def __reset_value(self, section, key, key_type):
        gsettings = getattr(self, section.replace('-','_') + '_gsettings')
        gsettings.reset(key)

    def load_from_gsettings(self):
        ''' Load settings from this app's GSettings '''
        for key_item in self.__key_list:
            self.__load_value(**key_item)

    def save_settings(self):
        ''' Save settings to GSettings of this app '''
        for key_item in self.__key_list:
            self.__save_value(**key_item)

    def get_setting_css(self) -> str:
        ''' Get CSS for current settings (to append to theme's 'gnome-shell.css' resource)

            target: either 'login' or 'session'
        '''

        css = "\n/* 'Login Manager Settings' App Provided CSS */\n"
        ### Background ###
        if self.background_type == "image" and self.background_image:
            css += "#lockDialogGroup {\n"
            css += "  background-image: url('resource:///org/gnome/shell/theme/background');\n"
            css += "  background-size: cover;\n"
            css += "}\n"
        elif self.background_type == "color":
            css += "#lockDialogGroup { background-color: "+ self.background_color + "; }\n"

        ### Top Bar ###
        def select_elem(elem:str='') -> str:
            if elem:
                return f"#panel .{elem}, #panel.login-screen .{elem}, #panel.unlock-screen .{elem}"
            else:
                return f"#panel, #panel.login-screen, #panel.unlock-screen"

        # Arrows
        if self.disable_top_bar_arrows:
            css += select_elem("popup-menu-arrow") + " { width: 0px; }\n"
        # Rounded Corners
        if self.disable_top_bar_rounded_corners:
            css +=  select_elem("panel-corner")
            css +=  " {\n"
            css += f"  -panel-corner-opacity: 0;\n"
            css +=  "}\n"
        # Text Color
        if self.change_top_bar_text_color:
            css +=  select_elem('panel-button')
            css +=  " {\n"
            css += f"  color: {self.top_bar_text_color};\n"
            css +=  "}\n"
        # Background Color
        if self.change_top_bar_background_color:
            css +=  select_elem()
            css +=  " {\n"
            css += f"  background-color: {self.top_bar_background_color};\n"
            css +=  "}\n"
            if not self.disable_top_bar_rounded_corners:
                css +=  select_elem("panel-corner")
                css +=  " {\n"
                css += f"  -panel-corner-opacity: 1;\n"
                css += f"  -panel-corner-background-color: {self.top_bar_background_color};\n"
                css +=  "}\n"
        return css

    def apply_shell_theme_settings(self):
        ''' Apply settings that require modification of 'gnome-shell-theme.gresource' file '''

        # back up the default shell theme (if needed)

        if self.gresource_utils.get_default():  # We can back up the default theme only if it exists on the system
            pure_theme_exists = path.exists(env.HOST_ROOT + self.gresource_utils.ThemesDir + '/default-pure')

            if self.gresource_utils.is_default(self.gresource_utils.ShellGresourceFile) or not pure_theme_exists:
                logging.info(_("Backing up default shell theme …"))

                if self.gresource_utils.is_default(self.gresource_utils.ShellGresourceFile):
                    self.command_elevator.add(f"cp {self.gresource_utils.ShellGresourceFile} {self.gresource_utils.ShellGresourceAutoBackup}")

                from os import makedirs
                makedirs(env.TEMP_DIR, exist_ok=True)

                self.gresource_utils.extract_default_shell_theme(f'{env.TEMP_DIR}/default-pure')

                self.command_elevator.add(f"rm -rf {self.gresource_utils.ThemesDir}/default-pure")
                self.command_elevator.add(f"mkdir -p {self.gresource_utils.ThemesDir}")
                self.command_elevator.add(f"cp -r {env.TEMP_DIR}/default-pure -t {self.gresource_utils.ThemesDir}")

        # Apply shell theme settings

        theme_path = None
        from .theme_lists import shell_themes
        for theme in shell_themes:
            if theme.name == self.shell_theme:
                theme_path = theme.path
                break

        shelldir = path.join(theme_path, 'gnome-shell') if theme_path else None
        background_image=None
        if self.background_type == "image" and self.background_image:
            background_image = self.background_image

        compiled_file = self.gresource_utils.compile(shelldir,
              additional_css=self.get_setting_css(),
            background_image=background_image
        )

        # We need to copy the compiled gresource file instead of moving it because the copy gets correct
        # SELinux context/label where applicable and prevents breakage of GDM in such situations.
        if self.gresource_utils.UbuntuGdmGresourceFile:
            logging.info(C_('Command-line output', "Applying GResource settings for Ubuntu …"))
            self.command_elevator.add(f"cp {compiled_file} {self.gresource_utils.CustomGresourceFile}")
            self.command_elevator.add(f"chown root: {self.gresource_utils.CustomGresourceFile}")
            self.command_elevator.add(f"chmod 644 {self.gresource_utils.CustomGresourceFile}")
            self.command_elevator.add(f'update-alternatives --quiet --install {self.gresource_utils.UbuntuGdmGresourceFile} {path.basename(self.gresource_utils.UbuntuGdmGresourceFile)} {self.gresource_utils.CustomGresourceFile} 0')
            self.command_elevator.add(f'update-alternatives --quiet --set {path.basename(self.gresource_utils.UbuntuGdmGresourceFile)} {self.gresource_utils.CustomGresourceFile}')
        else:
            logging.info(C_('Command-line output', "Applying GResource settings for non-Ubuntu systems …"))
            self.command_elevator.add(f"cp {compiled_file} {self.gresource_utils.ShellGresourceFile}")
            self.command_elevator.add(f"chown root: {self.gresource_utils.ShellGresourceFile}")
            self.command_elevator.add(f"chmod 644 {self.gresource_utils.ShellGresourceFile}")

    def apply_dconf_settings(self):
        ''' Apply settings that are applied through 'dconf' '''

        gdm_conf_dir = "/etc/dconf/db/gdm.d"
        gdm_profile_dir = "/etc/dconf/profile"
        gdm_profile_path = f"{gdm_profile_dir}/gdm"

        temp_profile_path = f"{env.TEMP_DIR}/gdm-profile"
        with open(temp_profile_path, "w+") as temp_profile_file:
            gdm_profile_contents  = "user-db:user\n"
            gdm_profile_contents += "system-db:gdm\n"
            gdm_profile_contents += "file-db:/usr/share/gdm/greeter-dconf-defaults"
            print(gdm_profile_contents, file=temp_profile_file)

        night_light_schedule_from  = self.night_light_start_hour
        night_light_schedule_from += self.night_light_start_minute / 60
        night_light_schedule_to  = self.night_light_end_hour
        night_light_schedule_to += self.night_light_end_minute / 60 

        temp_conf_path = f"{env.TEMP_DIR}/95-gdm-settings"
        with open(temp_conf_path, "w+") as temp_conf_file:
            gdm_conf_contents  =  "#-------- Interface ---------\n"
            gdm_conf_contents +=  "[org/gnome/desktop/interface]\n"
            gdm_conf_contents +=  "#----------------------------\n"
            gdm_conf_contents += f"cursor-theme='{self.cursor_theme}'\n"
            gdm_conf_contents += f"icon-theme='{self.icon_theme}'\n"
            gdm_conf_contents += f"show-battery-percentage={str(self.show_battery_percentage).lower()}\n"
            gdm_conf_contents += f"clock-show-seconds={str(self.show_seconds).lower()}\n"
            gdm_conf_contents += f"clock-show-weekday={str(self.show_weekday).lower()}\n"
            gdm_conf_contents += f"clock-format='{self.time_format}'\n"
            gdm_conf_contents += f"font-name='{self.font}'\n"
            gdm_conf_contents += f"font-antialiasing='{self.antialiasing}'\n"
            gdm_conf_contents += f"font-hinting='{self.hinting}'\n"
            gdm_conf_contents += f"text-scaling-factor={self.scaling_factor}\n"
            gdm_conf_contents +=  "\n"
            gdm_conf_contents +=  "#-------- Sound ---------\n"
            gdm_conf_contents +=  "[org/gnome/desktop/sound]\n"
            gdm_conf_contents +=  "#------------------------\n"
            gdm_conf_contents += f"theme-name='{self.sound_theme}'\n"
            gdm_conf_contents += f"event-sounds={str(self.event_sounds).lower()}\n"
            gdm_conf_contents += f"input-feedback-sounds={str(self.feedback_sounds).lower()}\n"
            gdm_conf_contents += f"allow-volume-above-100-percent={str(self.over_amplification).lower()}\n"
            gdm_conf_contents +=  "\n"
            gdm_conf_contents +=  "#-------------- Mouse ---------------\n"
            gdm_conf_contents +=  "[org/gnome/desktop/peripherals/mouse]\n"
            gdm_conf_contents +=  "#------------------------------------\n"
            gdm_conf_contents += f"accel-profile='{self.pointer_acceleration}'\n"
            gdm_conf_contents += f"natural-scroll={str(self.inverse_scrolling).lower()}\n"
            gdm_conf_contents += f"speed={self.mouse_speed}\n"
            gdm_conf_contents +=  "\n"
            gdm_conf_contents +=  "#-------------- Touchpad ---------------\n"
            gdm_conf_contents +=  "[org/gnome/desktop/peripherals/touchpad]\n"
            gdm_conf_contents +=  "#---------------------------------------\n"
            gdm_conf_contents += f"speed={self.touchpad_speed}\n"
            gdm_conf_contents += f"tap-to-click={str(self.tap_to_click).lower()}\n"
            gdm_conf_contents += f"natural-scroll={str(self.natural_scrolling).lower()}\n"
            gdm_conf_contents += f"two-finger-scrolling-enabled={str(self.two_finger_scrolling).lower()}\n"
            gdm_conf_contents += f"disable-while-typing={str(self.disable_while_typing).lower()}\n"
            gdm_conf_contents +=  "\n"
            gdm_conf_contents +=  "#------------- Night Light --------------\n"
            gdm_conf_contents +=  "[org/gnome/settings-daemon/plugins/color]\n"
            gdm_conf_contents +=  "#----------------------------------------\n"
            gdm_conf_contents += f"night-light-enabled={str(self.night_light_enabled).lower()}\n"
            gdm_conf_contents += f"night-light-temperature=uint32 {round(self.night_light_temperature)}\n"
            gdm_conf_contents += f"night-light-schedule-automatic={str(self.night_light_schedule_automatic).lower()}\n"
            gdm_conf_contents += f"night-light-schedule-from={night_light_schedule_from}\n"
            gdm_conf_contents += f"night-light-schedule-to={night_light_schedule_to}\n"
            gdm_conf_contents +=  "\n"
            gdm_conf_contents +=  "#----- Login Screen ----\n"
            gdm_conf_contents +=  "[org/gnome/login-screen]\n"
            gdm_conf_contents +=  "#-----------------------\n"
            gdm_conf_contents += f"logo='{self.logo.removeprefix(env.HOST_ROOT) if self.enable_logo else ''}'\n"
            gdm_conf_contents += f"banner-message-enable={str(self.enable_welcome_message).lower()}\n"
            gdm_conf_contents +=  "banner-message-text='"+self.welcome_message.replace("'", "\\'")+"'\n"
            gdm_conf_contents += f"disable-restart-buttons={str(self.disable_restart_buttons).lower()}\n"
            gdm_conf_contents += f"disable-user-list={str(self.disable_user_list).lower()}\n"

            print(gdm_conf_contents, file=temp_conf_file)

        self.command_elevator.add(f"mkdir -p '{gdm_conf_dir}' '{gdm_profile_dir}'")
        self.command_elevator.add(f"cp -f '{temp_conf_path}' -t '{gdm_conf_dir}'")
        self.command_elevator.add(f"cp -fT '{temp_profile_path}' '{gdm_profile_path}'")
        self.command_elevator.add("dconf update")

    def apply_settings(self) -> bool:
        ''' Apply all settings '''

        self.apply_shell_theme_settings()
        self.apply_dconf_settings()

        if self.command_elevator.run():
            # When we change GDM shell theme it becomes the 'default' theme but for the users
            # who didn't want to change shell theme for their session, we need to set it to a
            # pure/original version of the default shell theme
            # Note: We don't want to change user's shell theme if user set it explicitly to
            # 'default' in order to match their GDM theme
            if user_theme_settings := self._settings('org.gnome.shell.extensions.user-theme'):
                if user_theme_settings.get_string('name') == '' \
                and self.main_gsettings.get_boolean("never-applied"):
                    user_theme_settings.set_string('name', 'default-pure')

            self.save_settings()
            self.main_gsettings.set_boolean("never-applied", False)
            return True

        return False

    def apply_current_display_settings(self) -> bool:
        ''' Apply current display settings '''

        self.command_elevator.add(' '.join(['eval', 'install', '-Dm644',
                                            '~$(logname)/.config/monitors.xml',
                                            f'~{self.gresource_utils.GdmUsername}/.config/monitors.xml',
                                           ]))
        self.command_elevator.add(' '.join(['chown', f'{self.gresource_utils.GdmUsername}:',
                                            f'~{self.gresource_utils.GdmUsername}/.config/monitors.xml',
                                           ]))
        return self.command_elevator.run()

    def reset_settings(self) -> bool:
        status = False

        if self.gresource_utils.UbuntuGdmGresourceFile:
            logging.info(C_('Command-line output', "Resetting GResource settings for Ubuntu …"))
            self.command_elevator.add(' '.join(['update-alternatives',  '--quiet',  '--remove',
                                                 path.basename(self.gresource_utils.UbuntuGdmGresourceFile),
                                                 self.gresource_utils.CustomGresourceFile,
                                               ]))
            self.command_elevator.add(f'rm -f {self.gresource_utils.CustomGresourceFile}')
        elif path.exists(self.gresource_utils.ShellGresourceAutoBackup):
            logging.info(C_('Command-line output', "Resetting GResource settings for non-Ubuntu systems …"))
            self.command_elevator.add(' '.join(['mv', '-f',
                                                self.gresource_utils.ShellGresourceAutoBackup,
                                                self.gresource_utils.ShellGresourceFile,
                                               ]))
            self.command_elevator.add(f"chown root: {self.gresource_utils.ShellGresourceFile}")
            self.command_elevator.add(f"chmod 644 {self.gresource_utils.ShellGresourceFile}")

        self.command_elevator.add("rm -f /etc/dconf/profile/gdm")
        self.command_elevator.add("rm -f /etc/dconf/db/gdm.d/95-gdm-settings")
        self.command_elevator.add("dconf update")

        if self.command_elevator.run():
            for key_item in self.__key_list:
                self.__reset_value(**key_item)
            self.main_gsettings.reset("never-applied")

            self.load_settings()
            status = True

        return status

    def get_overriding_files(self):
        from os import listdir

        gdm_conf_dir = "/etc/dconf/db/gdm.d"
        overriding_files = []

        if path.isdir (env.HOST_ROOT + gdm_conf_dir):
            files = set (listdir (env.HOST_ROOT + gdm_conf_dir))
            files.add ('95-gdm-settings')
            files = sorted (files)
            index_of_next_file = files.index('95-gdm-settings') + 1
            overriding_files = files[index_of_next_file:]

        return overriding_files

    def cleanup(self):
        from shutil import rmtree
        rmtree(path=env.TEMP_DIR, ignore_errors=True)
