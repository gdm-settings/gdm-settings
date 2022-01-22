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
        self.load_from_gsettings()
    
    def load_from_gsettings(self):
        self.theme = self.gsettings.get_string("theme")
        self.background_type = self.gsettings.get_string("background-type")
        self.background_image = self.gsettings.get_string("background-image")
        self.background_color = self.gsettings.get_string("background-color")
        self.enabled_tweaks = self.gsettings.get_string("enabled-tweaks")
        self.custom_css = self.gsettings.get_string("custom-css")

    def save_to_gsettings(self):
        self.gsettings.set_string("theme", self.theme)
        self.gsettings.set_string("background-type", self.background_type)
        self.gsettings.set_string("background-image", self.background_image)
        self.gsettings.set_string("background-color", self.background_color)
        self.gsettings.set_string("enabled-tweaks", self.enabled_tweaks)
        self.gsettings.set_string("custom-css", self.custom_css)
    
    def get_setting_css(self) -> str:
        css = "\n/* 'GDM Settings' App Provided CSS */\n"
        if self.background_type == "Image":
            css += "#lockDialogGroup {\n"
            css += "  background-image: url('file://"+ self.background_image + "');\n"
            css += "  background-size: cover;\n"
            css += "}"
        elif self.background_type == "Color":
            css += "#lockDialogGroup { background-color: "+ self.background_color + "; }\n"
        css += "\n/* User-Provided CSS */\n"
        css += self.custom_css
        return css

    def apply_settings(self, elevator="pkexec"):
        auto_backup()
        os.makedirs(TempDir, exist_ok=True)
        shelldir = None
        if self.theme != "default":
            shelldir = f"/usr/share/themes/{self.theme}/gnome-shell"
        compiled_file = compile_theme(shellDir=shelldir, additional_css=self.get_setting_css())
        returncode = subprocess.run(args=[elevator, 'mv',compiled_file, GdmGresourceFile]).returncode
        if returncode == 0:
            self.save_to_gsettings()
