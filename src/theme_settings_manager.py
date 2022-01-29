'''Theme Settings Manager'''

import os
import subprocess
import gi

gi.require_version("Gio", '2.0')
from gi.repository import Gio

from info import *
from functions import *

class ThemeSettings():
    def __init__(self):
        self.gsettings = Gio.Settings(schema_id=application_id)
        self.theme_tweaks_gsettings = self.gsettings.get_child("theme-tweaks")
        self.load_from_gsettings()
    
    def load_from_gsettings(self):
        self.theme = self.gsettings.get_string("theme")
        self.background_type = self.gsettings.get_string("background-type")
        self.background_image = self.gsettings.get_string("background-image")
        self.background_color = self.gsettings.get_string("background-color")
        self.disable_top_bar_arrows = self.theme_tweaks_gsettings.get_boolean("disable-top-bar-arrows")
        self.change_top_bar_text_color = self.theme_tweaks_gsettings.get_boolean("change-top-bar-text-color")
        self.top_bar_text_color = self.theme_tweaks_gsettings.get_string("top-bar-text-color")
        self.change_top_bar_background_color = self.theme_tweaks_gsettings.get_boolean("change-top-bar-background-color")
        self.top_bar_background_color = self.theme_tweaks_gsettings.get_string("top-bar-background-color")

    def save_to_gsettings(self):
        self.gsettings.set_string("theme", self.theme)
        self.gsettings.set_string("background-type", self.background_type)
        self.gsettings.set_string("background-image", self.background_image)
        self.gsettings.set_string("background-color", self.background_color)
        self.theme_tweaks_gsettings.set_boolean("disable-top-bar-arrows", self.disable_top_bar_arrows)
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
            css +=  "#panel .panel-corner {\n"
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
        if elevated_commands_list.run():
            self.save_to_gsettings()
