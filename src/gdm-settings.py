#!/usr/bin/env python3
import gi, sys, os.path
gi.require_version("Gtk", '4.0')
gi.require_version("Gio", '2.0')
from gi.repository import Gtk

from functions import set_theme
from get_theme_list import get_theme_list

# Empty class to store arbitrary function arguments
class namespace:
    pass

args = namespace()
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
        self.builder = Gtk.Builder.new_from_file(os.path.join(script_dir, "main-window.ui"))
        self.win = self.builder.get_object("window_main")
        self.combobox = self.builder.get_object("combobox")
        self.refresh_combobox_entries(self.combobox)

    def connect_signals(self):
        self.connect("activate", self.on_activate)
        self.builder.get_object("button_quit").connect("clicked", self.close_window)
        self.builder.get_object("button_set_theme").connect("clicked", self.call_set_theme)
        #self.combobox.connect("popup", self.refresh_combobox_entries)
        
    def on_activate(self, something=None):
        self.add_window(self.win)
        self.win.present()

    def print_button_label(self, button):
        print(button.get_label())
    
    def refresh_combobox_entries(self, combobox):
        self.combobox.remove_all()
        for theme in get_theme_list():
            self.combobox.append_text(theme)
        self.combobox.remove(0)
        
    def close_window(self, widget=None):
        self.win.destroy()
        
    def call_set_theme(self, widget=None):
        args.askpass = "pkexec"
        args.re_apply = False
        args.opt_background = False
        args.background = False
        args.theme = self.combobox.get_active_text()
        try:
            set_theme(args)
        except TypeError:
            self.builder.add_from_file(os.path.join(script_dir, "error-dialog.ui"))
            dialog = self.builder.get_object("dialog_error")
            def destroy_dialog(self, *args, **kwargs):
                dialog.destroy()
            dialog.connect("response", destroy_dialog)
            dialog.present()

if __name__ == '__main__':
    MyApplication().run()
