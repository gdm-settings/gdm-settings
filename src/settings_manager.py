'''Settings Manager'''

from glob import glob
from subprocess import run, getoutput
from os import path, listdir, makedirs, remove, chmod
from shutil import copy, move, copytree, rmtree
from math import trunc

from .info import project_name, application_id

import gi
gi.require_version("Gio", '2.0')
from gi.repository import Gio

TempDir   = f'/tmp/{project_name}'
ConfigDir = f'/etc/{project_name}'

def __get_theme_list(themes_directory:str, decider:str, initial_list:list[str]):
    List = initial_list
    for dir in sorted(glob(f"{themes_directory}/*"), key=str.casefold):
        if path.exists(dir + f"/{decider}"):
            List.append(path.basename(dir))
    return List

def get_shell_theme_list():
    """get a list of installed gnome-shell/GDM themes"""
    return __get_theme_list(themes_directory='/usr/share/themes',
                            decider='gnome-shell/gnome-shell.css',
                            initial_list=['default'])

def get_sound_theme_list():
    """get a list of installed sound themes"""
    return __get_theme_list(themes_directory='/usr/share/sounds',
                            decider='index.theme',
                            initial_list=[])

def get_icon_theme_list():
    """get a list of installed icon themes"""
    return __get_theme_list(themes_directory='/usr/share/icons',
                            decider='index.theme',
                            initial_list=[])

def get_cursor_theme_list():
    """get a list of installed cursor themes"""
    return __get_theme_list(themes_directory='/usr/share/icons',
                            decider='cursors',
                            initial_list=[])

class CommandElevator:
    """ Runs a list of commands with elevated privilages """
    def __init__(self) -> None:
        self.__list = []
        self.__shebang = "#!/bin/sh"
        self.__elevator = "pkexec"

    def shebang(self, shebang:str=None):
        """ Shebang to determine shell for running elevated commands """
        if shebang:
            self.__shebang = shebang
        else:
            return self.__shebang

    def elevator(self, elevator:str=None):
        """
        Program to use for privilage elevation 
        
        Example: "sudo", "doas", "pkexec", etc.
        """
        if elevator:
            self.__elevator = elevator
        else:
            return self.__elevator

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
            makedirs(name=TempDir, exist_ok=True)
            script_file = f"{TempDir}/run-elevated"
            with open(script_file, "w") as open_script_file:
                print(self.__shebang, *self.__list, sep="\n", file=open_script_file)
            chmod(path=script_file, mode=755)
            returncode = run(args=[self.__elevator, script_file]).returncode
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

    TempShellDir = f'{TempDir}/gnome-shell'
    ThemesDir = '/usr/share/themes'
    GnomeShellDir = '/usr/share/gnome-shell'
    GdmGresourceFile = f'{GnomeShellDir}/gnome-shell-theme.gresource'
    UbuntuGdmGresourceFile = f'{GnomeShellDir}/gdm3-theme.gresource'
    GdmGresourceManualBackup = f'{GdmGresourceFile}.bak'
    GdmGresourceAutoBackup = f'{GdmGresourceFile}.default'
    GdmBackground = f'{GnomeShellDir}/theme/gdm-background'
    GresourceBasename = 'gnome-shell-theme.gresource'
    CustomThemeIdentity = 'custom-theme'

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
            if getoutput(f"gresource list {gresourceFile} /org/gnome/shell/theme/gnome-shell.css"):
                if not getoutput(f"gresource list {gresourceFile} /org/gnome/shell/theme/{self.CustomThemeIdentity}"):
                    return True
        return False

    def get_default(self) -> str:
        """get full path to the GResource file of the default theme (if the file exists)"""

        for file in self.GdmGresourceFile, self.GdmGresourceAutoBackup, self.GdmGresourceManualBackup:
           if self.is_default(file):
               return file

    def extract_theme(self, gresource_file:str):
        """extracts theme resources from provided GResource file of the theme

        Returns: path to a directory inside which resources of the theme were extracted"""

        TempExtractedDir = f"{TempDir}/extracted"
        resource_list = getoutput(f"gresource list {gresource_file}").splitlines()
        for resource in resource_list:
            filename = resource.removeprefix("/org/gnome/shell/theme/")
            filepath = path.join(TempExtractedDir, filename)
            content = getoutput(f"gresource extract {gresource_file} {resource}")
            makedirs(path.dirname(filepath), exist_ok=True)
            with open(file=filepath, mode="w+") as open_file:
                open_file.write(content)
        return TempExtractedDir

    def extract_default_theme(self, name:str="default-extracted"):
        """extracts resources of the default theme and puts them in a structure so that
        they can be used as a gnome-shell/GDM theme"""

        source_shell_dir = self.extract_theme(gresource_file=self.get_default())
        target_theme_dir = f"{self.ThemesDir}/{name}"
        target_shell_dir = f"{target_theme_dir}/gnome-shell"
        self.command_elevator.add(f"rm -rf {target_theme_dir}")
        self.command_elevator.add(f"mkdir -p {target_theme_dir}")
        self.command_elevator.add(f"mv -T {source_shell_dir} {target_shell_dir}")

    def auto_backup(self):
        """backup the default theme's GResource file (only if needed)
        for its use as the 'default' theme"""

        default_gresource =  self.get_default()
        if default_gresource and default_gresource != self.GdmGresourceAutoBackup:
            print("saving default theme ...")
            self.command_elevator.add(f"cp {default_gresource} {self.GdmGresourceAutoBackup}")

    def backup_update(self):
        """update backup of the default theme's GResource file on demand
        for its use as a restore point for the 'default' theme"""

        default_gresource =  self.get_default()
        if default_gresource and default_gresource != self.GdmGresourceManualBackup:
            print("updating backup of default theme ...")
            self.command_elevator.add(f"cp {default_gresource} {self.GdmGresourceManualBackup}")

    def backup_restore(self):
        """restore the 'default' theme's GResource file from the manually created backup"""

        if  path.isfile(self.GdmGresourceManualBackup):
            print("restoring default theme from backup ...")
            self.command_elevator.add(f"cp {self.GdmGresourceManualBackup} {self.GdmGresourceAutoBackup}")

    def compile(self, shellDir:str, additional_css:str):
        """Compile a theme into a GResource file for its use as the GDM theme"""

        # Remove temporary directory if already exists
        if path.exists(self.TempShellDir):
            rmtree(self.TempShellDir)
        tempGresourceFile = path.join(TempDir, 'gnome-shell-theme.gresource')
        # Remove temporary file if already exists
        if path.exists(tempGresourceFile):
            remove(tempGresourceFile)
        # Copy default resources to temporary directory
        copytree(self.extract_theme(self.get_default()), self.TempShellDir)
        # Copy gnome-shell dir of theme to temporary directory
        if shellDir:
            copytree(shellDir, self.TempShellDir, dirs_exist_ok=True)
        # Inject custom-theme identity
        open(path.join(self.TempShellDir, self.CustomThemeIdentity), 'w').close()
        # Background CSS
        with open(f"{self.TempShellDir}/gnome-shell.css", "a") as shell_css:
            print(additional_css, file=shell_css)
            pass

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
        move(path.join(self.TempShellDir,'gnome-shell-theme.gresource'), TempDir)
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

        ## Touchpad ##
        {section:"touchpad", key:'tap-to-click', key_type:"boolean"},
        {section:"touchpad", key:'natural-scrolling', key_type:"boolean"},
        {section:"touchpad", key:'two-finger-scrolling', key_type:"boolean"},
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
        self.touchpad_gsettings = Gio.Settings(schema_id=f'{application_id}.touchpad')
        self.night_light_gsettings = Gio.Settings(schema_id=f'{application_id}.night-light')
        self.misc_gsettings = Gio.Settings(schema_id=f'{application_id}.misc')

        self.load_settings()

    def load_settings(self):
        ''' Load settings '''

        self.load_from_gsettings()

        if self.main_gsettings.get_boolean("never-applied"):
            self.load_user_settings()

    def load_user_settings(self):
        ''' Load settings from user's session '''

        interface_settings = Gio.Settings(schema_id="org.gnome.desktop.interface")
        sound_settings = Gio.Settings(schema_id="org.gnome.desktop.sound")
        touchpad_settings = Gio.Settings(schema_id="org.gnome.desktop.peripherals.touchpad")
        night_light_settings = Gio.Settings(schema_id="org.gnome.settings-daemon.plugins.color")

        # Appearance
        self.icon_theme = interface_settings.get_string("icon-theme")
        self.cursor_theme = interface_settings.get_string("cursor-theme")
        # Fonts
        self.font = interface_settings.get_string("font-name")
        self.antialiasing = interface_settings.get_string("font-antialiasing")
        self.hinting = interface_settings.get_string("font-hinting")
        self.scaling_factor = interface_settings.get_double("text-scaling-factor")
        # Top Bar
        self.show_weekday = interface_settings.get_boolean("clock-show-weekday")
        self.time_format = interface_settings.get_string("clock-format")
        self.show_seconds = interface_settings.get_boolean("clock-show-seconds")
        self.show_battery_percentage = interface_settings.get_boolean("show-battery-percentage")
        # Sound
        self.sound_theme = sound_settings.get_string("theme-name")
        self.event_sounds = sound_settings.get_boolean("event-sounds")
        self.feedback_sounds = sound_settings.get_boolean("input-feedback-sounds")
        self.over_amplification = sound_settings.get_boolean("allow-volume-above-100-percent")
        # Touchpad
        self.tap_to_click = touchpad_settings.get_boolean("tap-to-click")
        self.natural_scrolling = touchpad_settings.get_boolean("natural-scroll")
        self.two_finger_scrolling = touchpad_settings.get_boolean("two-finger-scrolling-enabled")
        self.touchpad_speed = touchpad_settings.get_double("speed")
        # Night Light
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

    def __load_value(self, section, key, key_type):
        gsettings = getattr(self, section.replace('-','_') + '_gsettings')
        get_value = getattr(gsettings, 'get_' + key_type)
        setattr(self, key.replace('-','_'), get_value(key))

    def __save_value(self, section, key, key_type):
        gsettings = getattr(self, section.replace('-','_') + '_gsettings')
        set_value = getattr(gsettings, 'set_' + key_type)
        set_value(key, getattr(self, key.replace('-','_')))

    def load_from_gsettings(self):
        ''' Load settings from this app's GSettings '''
        for key_item in self.__key_list:
            self.__load_value(**key_item)

    def save_settings(self):
        ''' Save settings to GSettings of this app '''
        for key_item in self.__key_list:
            self.__save_value(**key_item)

    def get_setting_css(self) -> str:
        ''' Get CSS for current settings (to append to theme's 'gnome-shell.css' resource) '''

        css = "\n/* 'GDM Settings' App Provided CSS */\n"
        ### Background ###
        if self.background_type == "Image":
            css += "#lockDialogGroup {\n"
            css += "  background-image: url('file://"+ self.background_image + "');\n"
            css += "  background-size: cover;\n"
            css += "}\n"
        elif self.background_type == "Color":
            css += "#lockDialogGroup { background-color: "+ self.background_color + "; }\n"

        ### Top Bar ###
        # Arrows
        if self.disable_top_bar_arrows:
            css += "#panel .popup-menu-arrow { width: 0px; }\n"
        # Rounded Corners
        if self.disable_top_bar_rounded_corners:
            css +=  "#panel .panel-corner {\n"
            css += f"  -panel-corner-opacity: 0;\n"
            css +=  "}\n"
        # Text Color
        if self.change_top_bar_text_color:
            css +=  "#panel .panel-button {\n"
            css += f"  color: {self.top_bar_text_color};\n"
            css +=  "}\n"
        # Background Color
        if self.change_top_bar_background_color:
            css +=  "#panel, #panel.unlock-screen, #panel.login-screen {\n"
            css += f"  background-color: {self.top_bar_background_color};\n"
            css +=  "}\n"
            if not self.disable_top_bar_rounded_corners:
                css +=  "#panel .panel-corner, #panel.unlock-screen .panel-corner, #panel.login-screen .panel-corner {\n"
                css += f"  -panel-corner-opacity: 1;\n"
                css += f"  -panel-corner-background-color: {self.top_bar_background_color};\n"
                css +=  "}\n"
        return css

    def apply_gresource_settings(self):
        ''' Apply settings that require modification of 'gnome-shell-theme.gresource' file '''

        gresource_utils.auto_backup()
        makedirs(TempDir, exist_ok=True)
        shelldir = None
        if self.shell_theme != "default":
            shelldir = f"/usr/share/themes/{self.shell_theme}/gnome-shell"
        compiled_file = gresource_utils.compile(shellDir=shelldir, additional_css=self.get_setting_css())
        self.command_elevator.add(f"mv {compiled_file} {gresource_utils.GdmGresourceFile}")

    def apply_dconf_settings(self):
        ''' Apply settings that are applied through 'dconf' '''

        gdm_conf_dir = "/etc/dconf/db/gdm.d"
        gdm_profile_dir = "/etc/dconf/profile"
        gdm_profile_path = f"{gdm_profile_dir}/gdm"

        temp_profile_path = f"{TempDir}/gdm-profile"
        with open(temp_profile_path, "w+") as temp_profile_file:
            gdm_profile_contents  = "user-db:user\n"
            gdm_profile_contents += "system-db:gdm\n"
            gdm_profile_contents += "file-db:/usr/share/gdm/greeter-dconf-defaults"
            print(gdm_profile_contents, file=temp_profile_file)

        night_light_schedule_from  = self.night_light_start_hour
        night_light_schedule_from += self.night_light_start_minute / 60
        night_light_schedule_to  = self.night_light_end_hour
        night_light_schedule_to += self.night_light_end_minute / 60 

        temp_conf_path = f"{TempDir}/95-gdm-settings"
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
            gdm_conf_contents +=  "#-------------- Touchpad ---------------\n"
            gdm_conf_contents +=  "[org/gnome/desktop/peripherals/touchpad]\n"
            gdm_conf_contents +=  "#---------------------------------------\n"
            gdm_conf_contents += f"speed={self.touchpad_speed}\n"
            gdm_conf_contents += f"tap-to-click={str(self.tap_to_click).lower()}\n"
            gdm_conf_contents += f"natural-scroll={str(self.natural_scrolling).lower()}\n"
            gdm_conf_contents += f"two-finger-scrolling-enabled={str(self.two_finger_scrolling).lower()}\n"
            gdm_conf_contents +=  "\n"
            gdm_conf_contents +=  "#------------- Night Light --------------\n"
            gdm_conf_contents +=  "[org/gnome/settings-daemon/plugins/color]\n"
            gdm_conf_contents +=  "#----------------------------------------\n"
            gdm_conf_contents += f"night-light-enabled={str(self.night_light_enabled).lower()}\n"
            gdm_conf_contents += f"night-light-temperature=uint32 {round(self.night_light_temperature)}\n"
            gdm_conf_contents += f"night-light-schedule-automatic={str(self.night_light_schedule_automatic).lower()}\n"
            gdm_conf_contents += f"night-light-schedule-from={night_light_schedule_from}\n"
            gdm_conf_contents += f"night-light-schedule-to={night_light_schedule_to}\n"

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
            self.save_settings()
            self.main_gsettings.set_boolean("never-applied", False)
            return True
        return False

    def cleanup(self):
        rmtree(path=TempDir, ignore_errors=True)
