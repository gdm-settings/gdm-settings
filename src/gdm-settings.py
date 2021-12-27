#!/usr/bin/env python3
import gi, sys, os.path
gi.require_version("Gtk", '4.0')
gi.require_version("Gio", '2.0')
from gi.repository import Gtk

from functions import get_theme_list, set_theme

# Empty class to store arbitrary function arguments
script_realpath = os.path.realpath(sys.argv[0])
script_basename = os.path.basename(script_realpath)
script_dir = os.path.dirname(script_realpath)


class MyApplication(Gtk.Application):
    def __init__(self) -> None:
        super().__init__()
        self.assign_members()
        self.connect_signals()
        self.set_properties()
        
    def set_properties(self):
        #print(*dir(self.props), sep="\n)")
        self.set_application_id("org.gnome.gdm-settings")
        
    def assign_members(self):
        main_window_ui_file = os.path.join(script_dir, "main-window.ui")
        self.builder = Gtk.Builder.new_from_file(main_window_ui_file)
        self.window_main = self.builder.get_object("window_main")
        self.combobox = self.builder.get_object("combobox")
        self.refresh_combobox_entries(self.combobox)
        self.dialog_error = self.builder.get_object("dialog_error")

    def connect_signals(self):
        self.connect("activate", self.on_activate)
        self.builder.get_object("button_quit").connect("clicked", self.destroy_window)
        self.builder.get_object("button_set_theme").connect("clicked", self.call_set_theme)
        self.dialog_error.connect("response", self.hide_dialog)
        #self.combobox.connect("popup", self.refresh_combobox_entries)
        
    def on_activate(self, something=None):
        self.add_window(self.window_main)
        self.window_main.present()

    def print_button_label(self, button):
        print(button.get_label())
    
    def refresh_combobox_entries(self, combobox):
        combobox.remove_all()
        for theme in get_theme_list():
            combobox.append_text(theme)
        combobox.remove(0)
        
    def destroy_window(self, widget=None):
        self.window_main.destroy()

    def hide_dialog(self, widget, *args):
        widget.hide()
        
    def call_set_theme(self, widget=None):
        selected_theme = self.combobox.get_active_text()
        if selected_theme:
            set_theme(theme=selected_theme, askpass="pkexec")
        else:
            self.dialog_error.present()

if __name__ == '__main__':
    MyApplication().run()
