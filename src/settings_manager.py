'''Settings Manager'''

import os
import gi

gi.require_version("Gio", '2.0')
from gi.repository import Gio

from info import *
from functions import *

class GResourceSettings:
    def __init__(self):
        self.main_gsettings = Gio.Settings(schema_id=application_id)
        self.theme_tweaks_gsettings = Gio.Settings(schema_id=f"{application_id}.theme-tweaks")
        self.load_settings()
    
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
        auto_backup()
        os.makedirs(TempDir, exist_ok=True)
        shelldir = None
        if self.theme != "default":
            shelldir = f"/usr/share/themes/{self.theme}/gnome-shell"
        compiled_file = compile_theme(shellDir=shelldir, additional_css=self.get_setting_css())
        elevated_commands_list.add(f"mv {compiled_file} {GdmGresourceFile}")

class DConfSettings:
    def __init__(self):
        self.main_gsettings = Gio.Settings(schema_id=f"{application_id}")
        self.settings_gsettings = Gio.Settings(schema_id=f"{application_id}.settings")
        self.load_settings()


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

        elevated_commands_list.add(f"mkdir -p '{gdm_conf_dir}' '{gdm_profile_dir}'")
        elevated_commands_list.add(f"mv -f '{temp_conf_path}' -t '{gdm_conf_dir}'")
        elevated_commands_list.add(f"mv -fT '{temp_profile_path}' '{gdm_profile_path}'")
        elevated_commands_list.add("dconf update")

class Settings(GResourceSettings, DConfSettings):
    def __init__(self):
        self.main_gsettings = Gio.Settings(schema_id=application_id)
        self.theme_tweaks_gsettings = Gio.Settings(schema_id=f"{application_id}.theme-tweaks")
        self.settings_gsettings = Gio.Settings(schema_id=f"{application_id}.settings")
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
