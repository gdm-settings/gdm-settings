'''Settings Manager'''

from glob import glob
from subprocess import call, getoutput
from os import path, listdir, makedirs, remove
from shutil import copy, move, copytree, rmtree

import gi
gi.require_version("Gio", '2.0')
from gi.repository import Gio

from info import *
from command_elevation import ElevatedCommandsList

def __get_theme_list(themes_directory:str, decider:str, initial_list:list[str]):
    List = initial_list
    for dir in sorted(glob(f"{themes_directory}/*"), key=str.casefold):
        if path.exists(dir + f"/{decider}"):
            List.append(path.basename(dir))
    return List

def get_gdm_theme_list():
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

class GResourceUtils:
    def __init__(self):
        self.elevated_commands = ElevatedCommandsList()

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
                if not getoutput(f"gresource list {gresourceFile} /org/gnome/shell/theme/{CustomThemeIdentity}"):
                    return True
        return False

    def get_default(self) -> str:
        """get full path to the GResource file of the default theme (if the file exists)"""

        for file in GdmGresourceFile, GdmGresourceAutoBackup, GdmGresourceManualBackup:
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
        target_theme_dir = f"{ThemesDir}/{name}"
        target_shell_dir = f"{target_theme_dir}/gnome-shell"
        self.elevated_commands.add(f"rm -rf {target_theme_dir}")
        self.elevated_commands.add(f"mkdir -p {target_theme_dir}")
        self.elevated_commands.add(f"mv -T {source_shell_dir} {target_shell_dir}")

    def auto_backup(self):
        """backup the default theme's GResource file (only if needed)
        for its use as the 'default' theme"""

        default_gresource =  self.get_default()
        if default_gresource and default_gresource != GdmGresourceAutoBackup:
            print("saving default theme ...")
            self.elevated_commands.add(f"cp {default_gresource} {GdmGresourceAutoBackup}")

    def backup_update(self):
        """update backup of the default theme's GResource file on demand
        for its use as a restore point for the 'default' theme"""

        default_gresource =  self.get_default()
        if default_gresource and default_gresource != GdmGresourceManualBackup:
            print("updating backup of default theme ...")
            self.elevated_commands.add(f"cp {default_gresource} {GdmGresourceManualBackup}")

    def backup_restore(self):
        """restore the 'default' theme's GResource file from the manually created backup"""

        if  path.isfile(GdmGresourceManualBackup):
            print("restoring default theme from backup ...")
            self.elevated_commands.add(f"cp {GdmGresourceManualBackup} {GdmGresourceAutoBackup}")

    def compile(self, shellDir:str, additional_css:str):
        """Compile a theme into a GResource file for its use as the GDM theme"""

        # Remove temporary directory if already exists
        if path.exists(TempShellDir):
            rmtree(TempShellDir)
        tempGresourceFile = path.join(TempDir, 'gnome-shell-theme.gresource')
        # Remove temporary file if already exists
        if path.exists(tempGresourceFile):
            remove(tempGresourceFile)
        # Copy default resources to temporary directory
        copytree(self.extract_theme(self.get_default()), TempShellDir)
        # Copy gnome-shell dir of theme to temporary directory
        if shellDir:
            copytree(shellDir, TempShellDir, dirs_exist_ok=True)
        # Inject custom-theme identity
        open(path.join(TempShellDir, CustomThemeIdentity), 'w').close()
        # Background CSS
        with open(f"{TempShellDir}/gnome-shell.css", "a") as shell_css:
            print(additional_css, file=shell_css)
            pass

        # Copy gnome-shell.css to gdm.css and gdm3.css
        copy(src=f"{TempShellDir}/gnome-shell.css", dst=f"{TempShellDir}/gdm.css")
        copy(src=f"{TempShellDir}/gnome-shell.css", dst=f"{TempShellDir}/gdm3.css")

        # Open /tmp/gdm-settings/gnome-shell/gnome-shell-theme.gresource.xml for writing
        with open(path.join(TempShellDir, 'gnome-shell-theme.gresource.xml'), 'w') as GresourceXml:
            # Fill gnome-shell-theme.gresource.xml
            print('<?xml version="1.0" encoding="UTF-8"?>',
                  '<gresources>',
                  ' <gresource prefix="/org/gnome/shell/theme">',
                  sep='\n',
                  file=GresourceXml)
            for file in self.__listdir_recursive(TempShellDir):
                print('  <file>' + file + '</file>', file=GresourceXml)
            print(' </gresource>',
                  '</gresources>',
                  sep='\n',
                  file=GresourceXml)

        # Compile Theme
        call(f'glib-compile-resources --sourcedir={TempShellDir} {TempShellDir}/gnome-shell-theme.gresource.xml')
        move(path.join(TempShellDir,'gnome-shell-theme.gresource'), TempDir)
        rmtree(TempShellDir)
        return  tempGresourceFile

gresource_utils = GResourceUtils()

class Common:
    def __init__(self):
        self.elevated_commands = gresource_utils.elevated_commands
        self.main_gsettings = Gio.Settings(schema_id=application_id)

    def cleanup(self):
        rmtree(path=TempDir, ignore_errors=True)

class GResourceSettings(Common):
    def __init__(self):
        super().__init__()
        self.init()
        self.load_settings()

    def init(self):
        self.theme_tweaks_gsettings = Gio.Settings(schema_id=f"{application_id}.theme-tweaks")

    def load_settings(self):
        load_from_gsettings()

    def load_from_gsettings(self):
        self.theme = self.main_gsettings.get_string("theme")
        self.background_type = self.main_gsettings.get_string("background-type")
        self.background_image = self.main_gsettings.get_string("background-image")
        self.background_color = self.main_gsettings.get_string("background-color")
        self.disable_top_bar_arrows = self.theme_tweaks_gsettings.get_boolean("disable-top-bar-arrows")
        self.disable_top_bar_corners = self.theme_tweaks_gsettings.get_boolean("disable-top-bar-corners")
        self.change_top_bar_text_color = self.theme_tweaks_gsettings.get_boolean("change-top-bar-text-color")
        self.top_bar_text_color = self.theme_tweaks_gsettings.get_string("top-bar-text-color")
        self.change_top_bar_background_color = self.theme_tweaks_gsettings.get_boolean("change-top-bar-background-color")
        self.top_bar_background_color = self.theme_tweaks_gsettings.get_string("top-bar-background-color")

    def save_to_gsettings(self):
        self.main_gsettings.set_string("theme", self.theme)
        self.main_gsettings.set_string("background-type", self.background_type)
        self.main_gsettings.set_string("background-image", self.background_image)
        self.main_gsettings.set_string("background-color", self.background_color)
        self.theme_tweaks_gsettings.set_boolean("disable-top-bar-arrows", self.disable_top_bar_arrows)
        self.theme_tweaks_gsettings.set_boolean("disable-top-bar-corners", self.disable_top_bar_corners)
        self.theme_tweaks_gsettings.set_boolean("change-top-bar-text-color", self.change_top_bar_text_color)
        self.theme_tweaks_gsettings.set_string("top-bar-text-color", self.top_bar_text_color)
        self.theme_tweaks_gsettings.set_boolean("change-top-bar-background-color", self.change_top_bar_background_color)
        self.theme_tweaks_gsettings.set_string("top-bar-background-color", self.top_bar_background_color)

    def get_setting_css(self) -> str:
        css = "\n/* 'GDM Settings' App Provided CSS */\n"
        # Background
        if self.background_type == "Image":
            css += "#lockDialogGroup {\n"
            css += "  background-image: url('file://"+ self.background_image + "');\n"
            css += "  background-size: cover;\n"
            css += "}\n"
        elif self.background_type == "Color":
            css += "#lockDialogGroup { background-color: "+ self.background_color + "; }\n"
        # Disable Top Bar Arrows
        if self.disable_top_bar_arrows:
            css += "#panel .popup-menu-arrow { width: 0px; }\n"
        # Disable Top Bar Corners
        if self.disable_top_bar_corners:
            css +=  "#panel .panel-corner {\n"
            css += f"  -panel-corner-opacity: 0;\n"
            css +=  "}\n"
        # Change Top Bar Text Color
        if self.change_top_bar_text_color:
            css +=  "#panel .panel-button {\n"
            css += f"  color: {self.top_bar_text_color};\n"
            css +=  "}\n"
        # Change Top Bar Background Color
        if self.change_top_bar_background_color:
            css +=  "#panel, #panel.unlock-screen, #panel.login-screen {\n"
            css += f"  background-color: {self.top_bar_background_color};\n"
            css +=  "}\n"
            if not self.disable_top_bar_corners:
                css +=  "#panel .panel-corner, #panel.unlock-screen .panel-corner, #panel.login-screen .panel-corner {\n"
                css += f"  -panel-corner-opacity: 1;\n"
                css += f"  -panel-corner-background-color: {self.top_bar_background_color};\n"
                css +=  "}\n"
        return css

    def apply_settings(self):
        self.auto_backup()
        makedirs(TempDir, exist_ok=True)
        shelldir = None
        if self.theme != "default":
            shelldir = f"/usr/share/themes/{self.theme}/gnome-shell"
        compiled_file = self.compile(shellDir=shelldir, additional_css=self.get_setting_css())
        self.elevated_commands.add(f"mv {compiled_file} {GdmGresourceFile}")

class DConfSettings(Common):
    def __init__(self):
        super().__init__()
        self.init()
        self.load_settings()

    def init(self):
        self.settings_gsettings = Gio.Settings(schema_id=f"{application_id}.settings")

    def load_settings(self):
        if main_gsettings.get_boolean("first-run"):
            self.load_user_settings()
        else:
            self.load_from_gsettings()

    def load_user_settings(self):
        interface_settings = Gio.Settings(schema_id="org.gnome.desktop.interface")
        sound_settings = Gio.Settings(schema_id="org.gnome.desktop.sound")
        touchpad_settings = Gio.Settings(schema_id="org.gnome.desktop.peripherals.touchpad")
        night_light_settings = Gio.Settings(schema_id="org.gnome.settings-daemon.plugins.color")

        self.icon_theme = interface_settings.get_string("icon-theme")
        self.cursor_theme = interface_settings.get_string("cursor-theme")
        self.show_weekday = interface_settings.get_boolean("clock-show-weekday")
        self.time_format = interface_settings.get_string("clock-format")
        self.show_battery_percentage = interface_settings.get_boolean("show-battery-percentage")
        self.sound_theme = sound_settings.get_string("theme-name")
        self.tap_to_click = touchpad_settings.get_boolean("tap-to-click")
        self.touchpad_speed = touchpad_settings.get_double("speed")
        self.night_light_enabled = night_light_settings.get_boolean("night-light-enabled")
        self.night_light_schedule_automatic = night_light_settings.get_boolean("night-light-schedule-automatic")
        self.night_light_schedule_from = night_light_settings.get_double("night-light-schedule-from")
        self.night_light_schedule_to = night_light_settings.get_double("night-light-schedule-to")
        self.night_light_temperature = night_light_settings.get_uint("night-light-temperature")

    def load_from_gsettings(self):
        self.icon_theme = self.settings_gsettings.get_string('icon-theme')
        self.cursor_theme = self.settings_gsettings.get_string('cursor-theme')
        self.sound_theme = self.settings_gsettings.get_string('sound-theme')
        self.show_weekday = self.settings_gsettings.get_boolean('show-weekday')
        self.time_format = self.settings_gsettings.get_string('time-format')
        self.show_battery_percentage = self.settings_gsettings.get_boolean('show-battery-percentage')
        self.tap_to_click = self.settings_gsettings.get_boolean('tap-to-click')
        self.touchpad_speed = self.settings_gsettings.get_double('touchpad-speed')
        self.night_light_enabled = self.settings_gsettings.get_boolean('night-light-enabled')
        self.night_light_schedule_automatic = self.settings_gsettings.get_boolean('night-light-schedule-automatic')
        self.night_light_temperature = self.settings_gsettings.get_uint('night-light-temperature')
        self.night_light_schedule_from = self.settings_gsettings.get_double('night-light-schedule-from')
        self.night_light_schedule_to = self.settings_gsettings.get_double('night-light-schedule-to')

    def save_to_gsettings(self):
        self.settings_gsettings.set_string('icon-theme', self.icon_theme)
        self.settings_gsettings.set_string('cursor-theme', self.cursor_theme)
        self.settings_gsettings.set_string('sound-theme', self.sound_theme)
        self.settings_gsettings.set_boolean('show-weekday', self.show_weekday)
        self.settings_gsettings.set_string('time-format', self.time_format)
        self.settings_gsettings.set_boolean('show-battery-percentage', self.show_battery_percentage)
        self.settings_gsettings.set_boolean('tap-to-click', self.tap_to_click)
        self.settings_gsettings.set_double('touchpad-speed', self.touchpad_speed)
        self.settings_gsettings.set_boolean('night-light-enabled', self.night_light_enabled)
        self.settings_gsettings.set_boolean('night-light-schedule-automatic', self.night_light_schedule_automatic)
        self.settings_gsettings.set_uint('night-light-temperature', self.night_light_temperature)
        self.settings_gsettings.set_double('night-light-schedule-from', self.night_light_schedule_from)
        self.settings_gsettings.set_double('night-light-schedule-to', self.night_light_schedule_to)

    def apply_settings(self):
        gdm_conf_dir = "/etc/dconf/db/gdm.d"
        gdm_profile_dir = "/etc/dconf/profile"
        gdm_profile_path = f"{gdm_profile_dir}/gdm"

        temp_profile_path = f"{TempDir}/gdm-profile"
        with open(temp_profile_path, "w+") as temp_profile_file:
            gdm_profile_contents  = "user-db:user\n"
            gdm_profile_contents += "system-db:gdm\n"
            gdm_profile_contents += "file-db:/usr/share/gdm/greeter-dconf-defaults"
            print(gdm_profile_contents, file=temp_profile_file)

        temp_conf_path = f"{TempDir}/95-gdm-settings"
        with open(temp_conf_path, "w+") as temp_conf_file:
            gdm_conf_contents  =  "#-------- Interface ---------\n"
            gdm_conf_contents +=  "[org/gnome/desktop/interface]\n"
            gdm_conf_contents +=  "#----------------------------\n"
            gdm_conf_contents += f"cursor-theme='{self.cursor_theme}'\n"
            gdm_conf_contents += f"icon-theme='{self.icon_theme}'\n"
            gdm_conf_contents += f"show-battery-percentage={str(self.show_battery_percentage).lower()}\n"
            gdm_conf_contents += f"clock-show-weekday={str(self.show_weekday).lower()}\n"
            gdm_conf_contents += f"clock-format='{self.time_format}'\n"
            gdm_conf_contents +=  "\n"
            gdm_conf_contents +=  "#-------- Sound ---------\n"
            gdm_conf_contents +=  "[org/gnome/desktop/sound]\n"
            gdm_conf_contents +=  "#------------------------\n"
            gdm_conf_contents += f"theme-name='{self.sound_theme}'\n"
            gdm_conf_contents +=  "\n"
            gdm_conf_contents +=  "#-------------- Touchpad ---------------\n"
            gdm_conf_contents +=  "[org/gnome/desktop/peripherals/touchpad]\n"
            gdm_conf_contents +=  "#---------------------------------------\n"
            gdm_conf_contents += f"speed={self.touchpad_speed}\n"
            gdm_conf_contents += f"tap-to-click={str(self.tap_to_click).lower()}\n"
            gdm_conf_contents +=  "\n"
            gdm_conf_contents +=  "#------------- Night Light --------------\n"
            gdm_conf_contents +=  "[org/gnome/settings-daemon/plugins/color]\n"
            gdm_conf_contents +=  "#----------------------------------------\n"
            gdm_conf_contents += f"night-light-enabled={str(self.night_light_enabled).lower()}\n"
            gdm_conf_contents += f"night-light-temperature=uint32 {round(self.night_light_temperature)}\n"
            gdm_conf_contents += f"night-light-schedule-automatic={str(self.night_light_schedule_automatic).lower()}\n"
            gdm_conf_contents += f"night-light-schedule-from={self.night_light_schedule_from}\n"
            gdm_conf_contents += f"night-light-schedule-to={self.night_light_schedule_to}\n"

            print(gdm_conf_contents, file=temp_conf_file)

        self.elevated_commands.add(f"mkdir -p '{gdm_conf_dir}' '{gdm_profile_dir}'")
        self.elevated_commands.add(f"mv -f '{temp_conf_path}' -t '{gdm_conf_dir}'")
        self.elevated_commands.add(f"mv -fT '{temp_profile_path}' '{gdm_profile_path}'")
        self.elevated_commands.add("dconf update")

class Settings(GResourceSettings, DConfSettings):
    def __init__(self):
        Common.__init__(self)
        GResourceSettings.init(self)
        DConfSettings.init(self)
        self.load_settings()

    def load_settings(self):
        GResourceSettings.load_from_gsettings(self)
        if self.main_gsettings.get_boolean("first-run"):
            DConfSettings.load_user_settings(self)
        else:
            DConfSettings.load_from_gsettings(self)
    def load_from_gsettings(self):
        GResourceSettings.load_from_gsettings(self)
        DConfSettings.load_from_gsettings(self)
    def save_to_gsettings(self):
        GResourceSettings.save_to_gsettings(self)
        DConfSettings.save_to_gsettings(self)
    def apply_settings(self):
        GResourceSettings.apply_settings(self)
        DConfSettings.apply_settings(self)
