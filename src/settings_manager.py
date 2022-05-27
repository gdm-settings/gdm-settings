'''The actual settings manager'''

from glob import glob
from subprocess import run
from os import path, listdir, makedirs, remove, chmod
from shutil import copy, move, copytree, rmtree
from math import trunc

from gi.repository import Gio

from . import env
from .info import project_name, application_id
from .utils import getstdout

if env.PACKAGE_TYPE == env.PackageType.Flatpak:
    TEMP_DIR = path.join(env.XDG_CACHE_HOME, 'tmp') # ~/.var/app/io.github.realmazharhussain.GdmSettings/cache/tmp
else:
    TEMP_DIR = path.join(env.XDG_CACHE_HOME, project_name) # ~/.cache/gdm-settings

class Theme:
    def __init__(self, name:str, path:str):
        self.name = name
        self.path = path
    def __lt__(self, value, /):
        return self.name.casefold() < value.name.casefold()
    def __repr__(self):
        return f"Theme(name='{self.name}', path='{self.path}')"

def update_theme_list(type:str):
    temp_list = []

    if type == 'shell':
        dirname = 'themes'
        decider = 'gnome-shell'
        temp_list.append(Theme('default', None))
        theme_list = shell_themes
    elif type in ['sound', 'sounds']:
        dirname = 'sounds'
        decider = 'index.theme'
        theme_list = sound_themes
    elif type in ['icon', 'icons']:
        dirname = 'icons'
        decider = 'index.theme'
        theme_list = icon_themes
    elif type in ['cursor', 'cursors']:
        dirname = 'icons'
        decider = 'cursors'
        theme_list = cursor_themes
    else:
        raise ValueError(f"invalid type '{type}'")

    for data_dir in env.SYSTEM_DATA_DIRS:
        for theme_dir in glob(f"{env.HOST_ROOT}{data_dir}/{dirname}/*"):
            theme_name = path.basename(theme_dir)
            if path.exists(path.join(theme_dir, decider)) and theme_name not in [theme.name for theme in temp_list]:
                temp_list.append(Theme(theme_name, theme_dir))

    theme_list.clear()
    theme_list += sorted(temp_list)

def update_all_theme_lists():
    for type in 'shell', 'icons', 'cursors', 'sound':
        update_theme_list(type)

# Theme Lists
shell_themes  = []
icon_themes   = []
cursor_themes = []
sound_themes  = []
update_all_theme_lists()

class CommandElevator:
    """ Runs a list of commands with elevated privilages """
    def __init__(self, elevator:str=None, shebang:str=None) -> None:
        self.__list = []
        self.shebang = shebang or "#!/bin/sh"
        if elevator:
            self.elevator = elevator
        else:
            self.autodetect_elevator()

    @property
    def shebang(self):
        """ Shebang to determine shell for running elevated commands """
        return self.__shebang
    @shebang.setter
    def shebang(self, value):
        if value.startswith('#!/'):
            self.__shebang = value
        else:
            raise ValueError("shebang does not start with '#!/'")

    @property
    def elevator(self):
        """
        Program to use for privilage elevation 
        
        Example: "sudo", "doas", "pkexec", etc.
        """
        return self.__elevator
    @elevator.setter
    def elevator(self, value):
        if isinstance(value, str):
            self.__elevator = value.strip(' ').split(' ')
        elif isinstance(value, list):
            self.__elevator = value
        else:
            raise ValueError("elevator is not of type 'str' or 'list'")

    def autodetect_elevator(self):
        if env.INTERFACE_TYPE is env.InterfaceType.Graphical:
            if env.PACKAGE_TYPE is env.PackageType.Flatpak:
                self.elevator = "flatpak-spawn --host pkexec"
            else:
                self.elevator = "pkexec"
        else:
            if env.PACKAGE_TYPE is env.PackageType.Flatpak:
                self.elevator = "flatpak-spawn --host sudo"
            else:
                self.elevator = "sudo"

    def add(self, cmd:str):
        """ Add a new command to the list """
        return self.__list.append(cmd)

    def clear(self):
        """ Clear command list """
        return self.__list.clear()

    def run_only(self) -> bool:
        """ Run commands but DO NOT clear command list """
        returncode = 0
        if len(self.__list):
            makedirs(name=TEMP_DIR, exist_ok=True)
            script_file = f"{TEMP_DIR}/run-elevated"
            with open(script_file, "w") as open_script_file:
                print(self.__shebang, *self.__list, sep="\n", file=open_script_file)
            chmod(path=script_file, mode=755)
            returncode = run(args=[*self.__elevator, script_file]).returncode
            remove(script_file)
        # Return Code 0 of subprocess means success, but boolean with value 0 is interpreted as False
        # So, 'not returncode' boolean will be True when the subprocess succeeds
        return not returncode

    def run(self) -> bool:
        """ Run commands and clear command list"""
        status = self.run_only()
        self.clear()
        return status

class GResourceUtils:
    ''' Utilities (functions) for 'gnome-shell-theme.gresource' file '''

    CustomThemeIdentity = 'custom-theme'
    TempShellDir        = f'{TEMP_DIR}/gnome-shell'
    ThemesDir           = path.join(env.SYSTEM_DATA_DIRS[0], 'themes')
    GdmGresourceFile    = None
    CustomGresourceFile = None
    for data_dir in env.SYSTEM_DATA_DIRS:
        file = path.join(data_dir, 'gnome-shell', 'gnome-shell-theme.gresource')
        if path.isfile(env.HOST_ROOT + file):
            GdmGresourceFile    = file
            CustomGresourceFile = GdmGresourceFile + ".gdm_settings"
            break
    GdmGresourceAutoBackup = f'{GdmGresourceFile}.default'
    UbuntuGdmGresourceFile = None
    if path.isfile(env.HOST_ROOT + '/usr/share/gnome-shell/gdm-theme.gresource'):
        UbuntuGdmGresourceFile = '/usr/share/gnome-shell/gdm-theme.gresource'
    elif path.isfile(env.HOST_ROOT + '/usr/share/gnome-shell/gdm3-theme.gresource'):
        UbuntuGdmGresourceFile = '/usr/share/gnome-shell/gdm3-theme.gresource'

    def __init__(self, command_elevator:CommandElevator=None):
        if command_elevator:
            self.command_elevator = command_elevator
        else:
            self.command_elevator = CommandElevator()

    def __listdir_recursive(self, dir:str):
        """list files (only) inside a directory recursively"""

        files=[]
        for file in listdir(dir):
            if path.isdir(path.join(dir, file)):
                for subdir_file in self.__listdir_recursive(path.join(dir, file)):
                    files += [path.join(file, subdir_file)]
            else:
                files += [file]
        return files

    def is_default(self, gresourceFile:str):
        """checks if the provided file is a GResource file of the default theme"""

        if path.exists(gresourceFile):
            if getstdout(["gresource", "list", gresourceFile, "/org/gnome/shell/theme/gnome-shell.css"]):
                if not getstdout(f"gresource list {gresourceFile} /org/gnome/shell/theme/{self.CustomThemeIdentity}"):
                    return True
        return False

    def get_default(self) -> str:
        """get full path to the GResource file of the default theme (if the file exists)"""

        for file in self.GdmGresourceFile, self.GdmGresourceAutoBackup:
           if self.is_default(env.HOST_ROOT + file):
               return file

    def extract_theme(self, gresource_file:str):
        """extracts theme resources from provided GResource file of the theme

        Returns: path to a directory inside which resources of the theme were extracted"""

        TempExtractedDir = f"{TEMP_DIR}/extracted"
        resource_list = getstdout(["gresource", "list", gresource_file]).decode().splitlines()
        for resource in resource_list:
            filename = resource.removeprefix("/org/gnome/shell/theme/")
            filepath = path.join(TempExtractedDir, filename)
            content = getstdout(["gresource", "extract", gresource_file, resource])
            makedirs(path.dirname(filepath), exist_ok=True)
            with open(file=filepath, mode="wb") as open_file:
                open_file.write(content)
        return TempExtractedDir

    def extract_default_theme(self, target_dir:str=None, additional_css:str="", name:str="default-extracted"):
        """extracts resources of the default theme and puts them in a structure so that
        they can be used as a gnome-shell/GDM theme"""

        target_dir = target_dir or self.ThemesDir
        target_theme_dir = target_dir + "/" + name
        target_shell_dir = target_theme_dir + "/gnome-shell"
        source_shell_dir = self.extract_theme(gresource_file=env.HOST_ROOT+self.get_default())
        status = True

        if additional_css:
            with open(source_shell_dir + "/gnome-shell.css", "a") as shell_css:
                print(additional_css, file=shell_css)

        if run(['test', '-w', target_dir]).returncode == 0:
            if path.exists(target_theme_dir):
                rmtree(target_theme_dir)
            makedirs(target_theme_dir)
            copytree(source_shell_dir, target_shell_dir)
        else:
            self.command_elevator.add(f"rm -rf {target_theme_dir}")
            self.command_elevator.add(f"mkdir -p {target_theme_dir}")
            self.command_elevator.add(f"mv -T {source_shell_dir} {target_shell_dir}")
            status = self.command_elevator.run()

        return status

    def _extract_default_pure_theme(self):
        makedirs(TEMP_DIR, exist_ok=True)
        self.extract_default_theme(target_dir=TEMP_DIR, name='default-pure')
        self.command_elevator.add(f"rm -rf {self.ThemesDir}/default-pure")
        self.command_elevator.add(f"mkdir -p {self.ThemesDir}")
        self.command_elevator.add(f"mv -t {self.ThemesDir} {TEMP_DIR}/default-pure")

    def auto_backup(self):
        """backup the default theme's GResource file (only if needed)
        for its use as the 'default' theme"""

        default_gresource =  self.get_default()
        if default_gresource and default_gresource != self.GdmGresourceAutoBackup:
            print(_("saving default theme ..."))
            self.command_elevator.add(f"cp {default_gresource} {self.GdmGresourceAutoBackup}")
            self._extract_default_pure_theme()
        elif not path.exists(env.HOST_ROOT + self.ThemesDir + '/default-pure'):
            self._extract_default_pure_theme()

    def compile(self, shellDir:str, additional_css:str, background_image:str=None):
        """Compile a theme into a GResource file for its use as the GDM theme"""

        # Remove temporary directory if already exists
        if path.exists(self.TempShellDir):
            rmtree(self.TempShellDir)
        tempGresourceFile = path.join(TEMP_DIR, 'gnome-shell-theme.gresource')
        # Remove temporary file if already exists
        if path.exists(tempGresourceFile):
            remove(tempGresourceFile)
        # Copy default resources to temporary directory
        copytree(self.extract_theme(env.HOST_ROOT + self.get_default()), self.TempShellDir)
        # Copy gnome-shell dir of theme to temporary directory
        if shellDir:
            copytree(shellDir, self.TempShellDir, dirs_exist_ok=True)
        # Inject custom-theme identity
        open(path.join(self.TempShellDir, self.CustomThemeIdentity), 'w').close()
        # Background Image
        if background_image:
            copy(src=background_image, dst=path.join(self.TempShellDir, 'background'))
        # Additional CSS
        with open(f"{self.TempShellDir}/gnome-shell.css", "a") as shell_css:
            print(additional_css, file=shell_css)

        # Copy gnome-shell.css to gdm.css and gdm3.css
        copy(src=f"{self.TempShellDir}/gnome-shell.css", dst=f"{self.TempShellDir}/gdm.css")
        copy(src=f"{self.TempShellDir}/gnome-shell.css", dst=f"{self.TempShellDir}/gdm3.css")

        # Open /tmp/gdm-settings/gnome-shell/gnome-shell-theme.gresource.xml for writing
        with open(path.join(self.TempShellDir, 'gnome-shell-theme.gresource.xml'), 'w') as GresourceXml:
            # Fill gnome-shell-theme.gresource.xml
            print('<?xml version="1.0" encoding="UTF-8"?>',
                  '<gresources>',
                  ' <gresource prefix="/org/gnome/shell/theme">',
                  sep='\n',
                  file=GresourceXml)
            for file in self.__listdir_recursive(self.TempShellDir):
                print('  <file>' + file + '</file>', file=GresourceXml)
            print(' </gresource>',
                  '</gresources>',
                  sep='\n',
                  file=GresourceXml)

        # Compile Theme
        run(['glib-compile-resources', f'--sourcedir={self.TempShellDir}', f'{self.TempShellDir}/gnome-shell-theme.gresource.xml'])
        move(path.join(self.TempShellDir,'gnome-shell-theme.gresource'), TEMP_DIR)
        rmtree(self.TempShellDir)
        return  tempGresourceFile

gresource_utils = GResourceUtils()

class Settings:
    section = "section"
    key = "key"
    key_type = "key_type"

    __key_list = [
        ## Appearance ##
        {section:"appearance", key:"shell-theme", key_type:"string"},
        {section:"appearance", key:'icon-theme', key_type:"string"},
        {section:"appearance", key:'cursor-theme', key_type:"string"},
        {section:"appearance", key:"background-type", key_type:"string"},
        {section:"appearance", key:"background-image", key_type:"string"},
        {section:"appearance", key:"background-color", key_type:"string"},
        ## Fonts ##
        {section:"fonts", key:"font", key_type:"string"},
        {section:"fonts", key:"antialiasing", key_type:"string"},
        {section:"fonts", key:"hinting", key_type:"string"},
        {section:"fonts", key:"scaling-factor", key_type:"double"},

        ## Top Bar ##
        # Tweaks
        {section:"top-bar", key:"disable-top-bar-arrows", key_type:"boolean"},
        {section:"top-bar", key:"disable-top-bar-rounded-corners", key_type:"boolean"},
        {section:"top-bar", key:"change-top-bar-text-color", key_type:"boolean"},
        {section:"top-bar", key:"top-bar-text-color", key_type:"string"},
        {section:"top-bar", key:"change-top-bar-background-color", key_type:"boolean"},
        {section:"top-bar", key:"top-bar-background-color", key_type:"string"},
        # Time/Clock
        {section:"top-bar", key:'show-weekday', key_type:"boolean"},
        {section:"top-bar", key:'time-format', key_type:"string"},
        {section:"top-bar", key:'show-seconds', key_type:"boolean"},
        # Power
        {section:"top-bar", key:'show-battery-percentage', key_type:"boolean"},

        ## Sound ##
        {section:"sound", key:'sound-theme', key_type:"string"},
        {section:"sound", key:'event-sounds', key_type:"boolean"},
        {section:"sound", key:'feedback-sounds', key_type:"boolean"},
        {section:"sound", key:'over-amplification', key_type:"boolean"},

        ## Pointing ##
        # Mouse
        {section:"mouse", key:'pointer-acceleration', key_type:"string"},
        {section:"mouse", key:'inverse-scrolling', key_type:"boolean"},
        {section:"mouse", key:'mouse-speed', key_type:"double"},
        # Touchpad
        {section:"touchpad", key:'tap-to-click', key_type:"boolean"},
        {section:"touchpad", key:'natural-scrolling', key_type:"boolean"},
        {section:"touchpad", key:'two-finger-scrolling', key_type:"boolean"},
        {section:"touchpad", key:'disable-while-typing', key_type:"boolean"},
        {section:"touchpad", key:'touchpad-speed', key_type:"double"},

        ## Night Light ##
        {section:"night-light", key:'night-light-enabled', key_type:"boolean"},
        {section:"night-light", key:'night-light-schedule-automatic', key_type:"boolean"},
        {section:"night-light", key:'night-light-temperature', key_type:"uint"},
        {section:"night-light", key:'night-light-start-hour', key_type:"int"},
        {section:"night-light", key:'night-light-start-minute', key_type:"int"},
        {section:"night-light", key:'night-light-end-hour', key_type:"int"},
        {section:"night-light", key:'night-light-end-minute', key_type:"int"},

        ## Misc ##
        {section:"misc", key:"enable-welcome-message", key_type:"boolean"},
        {section:"misc", key:"welcome-message", key_type:"string"},
        {section:"misc", key:"enable-logo", key_type:"boolean"},
        {section:"misc", key:"logo", key_type:"string"},
        {section:"misc", key:"disable-restart-buttons", key_type:"boolean"},
        {section:"misc", key:"disable-user-list", key_type:"boolean"},
    ]

    def __init__(self):
        self.command_elevator = gresource_utils.command_elevator

        self.main_gsettings = Gio.Settings(schema_id=application_id)
        self.appearance_gsettings = Gio.Settings(schema_id=f'{application_id}.appearance')
        self.fonts_gsettings = Gio.Settings(schema_id=f'{application_id}.fonts')
        self.top_bar_gsettings = Gio.Settings(schema_id=f'{application_id}.top-bar')
        self.sound_gsettings = Gio.Settings(schema_id=f'{application_id}.sound')
        self.pointing_gsettings = Gio.Settings(schema_id=f'{application_id}.pointing')
        self.mouse_gsettings = Gio.Settings(schema_id=f'{application_id}.pointing.mouse')
        self.touchpad_gsettings = Gio.Settings(schema_id=f'{application_id}.pointing.touchpad')
        self.night_light_gsettings = Gio.Settings(schema_id=f'{application_id}.night-light')
        self.misc_gsettings = Gio.Settings(schema_id=f'{application_id}.misc')

        self.load_settings()

    def load_settings(self):
        ''' Load settings '''

        self.load_from_gsettings()

        if self.main_gsettings.get_boolean("never-applied") \
        and env.PACKAGE_TYPE is not env.PackageType.Flatpak:
            self.load_user_settings()

    def _settings(self, schema_id:str):
        if schema := Gio.SettingsSchemaSource.get_default().lookup(schema_id, recursive=True):
            return Gio.Settings(schema_id=schema_id)


    def load_user_settings(self):
        ''' Load settings from user's session '''


        if user_theme_settings := self._settings('org.gnome.shell.extensions.user-theme'):
            self.shell_theme = user_theme_settings.get_string('name')

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
        if self.background_type == "Image" and self.background_image:
            css += "#lockDialogGroup {\n"
            css += "  background-image: url('resource:///org/gnome/shell/theme/background');\n"
            css += "  background-size: cover;\n"
            css += "}\n"
        elif self.background_type == "Color":
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

    def apply_gresource_settings(self):
        ''' Apply settings that require modification of 'gnome-shell-theme.gresource' file '''

        gresource_utils.auto_backup()
        makedirs(TEMP_DIR, exist_ok=True)

        theme_path = None
        for theme in shell_themes:
            if theme.name == self.shell_theme:
                theme_path = theme.path
                break
        shelldir = path.join(theme_path, 'gnome-shell') if theme_path else None
        background_image=None
        if self.background_type == "Image" and self.background_image:
            background_image = self.background_image
        compiled_file = gresource_utils.compile(shelldir, additional_css=self.get_setting_css(), background_image=background_image)

        # We need to copy the compiled gresource file instead of moving it because the copy gets correct
        # SELinux context/label where applicable and prevents breakage of GDM in such situations.
        if gresource_utils.UbuntuGdmGresourceFile:
            self.command_elevator.add(f"cp {compiled_file} {gresource_utils.CustomGresourceFile}")
            self.command_elevator.add(f"chown root: {gresource_utils.CustomGresourceFile}")
            self.command_elevator.add(f"chmod 644 {gresource_utils.CustomGresourceFile}")
            self.command_elevator.add(f'update-alternatives --quiet --install {gresource_utils.UbuntuGdmGresourceFile} {path.basename(gresource_utils.UbuntuGdmGresourceFile)} {gresource_utils.CustomGresourceFile} 0')
            self.command_elevator.add(f'update-alternatives --quiet --set {path.basename(gresource_utils.UbuntuGdmGresourceFile)} {gresource_utils.CustomGresourceFile}')
        else:
            self.command_elevator.add(f"cp {compiled_file} {gresource_utils.GdmGresourceFile}")
            self.command_elevator.add(f"chown root: {gresource_utils.GdmGresourceFile}")
            self.command_elevator.add(f"chmod 644 {gresource_utils.GdmGresourceFile}")

    def apply_dconf_settings(self):
        ''' Apply settings that are applied through 'dconf' '''

        gdm_conf_dir = "/etc/dconf/db/gdm.d"
        gdm_profile_dir = "/etc/dconf/profile"
        gdm_profile_path = f"{gdm_profile_dir}/gdm"

        temp_profile_path = f"{TEMP_DIR}/gdm-profile"
        with open(temp_profile_path, "w+") as temp_profile_file:
            gdm_profile_contents  = "user-db:user\n"
            gdm_profile_contents += "system-db:gdm\n"
            gdm_profile_contents += "file-db:/usr/share/gdm/greeter-dconf-defaults"
            print(gdm_profile_contents, file=temp_profile_file)

        night_light_schedule_from  = self.night_light_start_hour
        night_light_schedule_from += self.night_light_start_minute / 60
        night_light_schedule_to  = self.night_light_end_hour
        night_light_schedule_to += self.night_light_end_minute / 60 

        temp_conf_path = f"{TEMP_DIR}/95-gdm-settings"
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
        self.command_elevator.add(f"mv -f '{temp_conf_path}' -t '{gdm_conf_dir}'")
        self.command_elevator.add(f"mv -fT '{temp_profile_path}' '{gdm_profile_path}'")
        self.command_elevator.add("dconf update")

    def apply_settings(self) -> bool:
        ''' Apply all settings '''

        self.apply_gresource_settings()
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

        self.command_elevator.add("eval install -Dm644 ~{$(logname),gdm}/.config/monitors.xml")
        self.command_elevator.add("chown gdm: ~gdm/.config/monitors.xml")
        return self.command_elevator.run()

    def reset_settings(self) -> bool:
        status = False

        if gresource_utils.UbuntuGdmGresourceFile:
            self.command_elevator.add(f'update-alternatives --quiet --remove {path.basename(gresource_utils.UbuntuGdmGresourceFile)} {gresource_utils.CustomGresourceFile}')
            self.command_elevator.add(f'rm -f {gresource_utils.CustomGresourceFile}')
        elif path.exists(gresource_utils.GdmGresourceAutoBackup):
                self.command_elevator.add(f"mv -f {gresource_utils.GdmGresourceAutoBackup} {gresource_utils.GdmGresourceFile}")
                self.command_elevator.add(f"chown root: {gresource_utils.GdmGresourceFile}")
                self.command_elevator.add(f"chmod 644 {gresource_utils.GdmGresourceFile}")

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

    def cleanup(self):
        rmtree(path=TEMP_DIR, ignore_errors=True)
