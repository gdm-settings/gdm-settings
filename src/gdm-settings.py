#!/usr/bin/env python3
import gi, sys, os.path

gi.require_version("Gtk", '4.0')
from gi.repository import Gtk

from functions import get_theme_list, set_theme

script_realpath = os.path.realpath(sys.argv[0])
script_basename = os.path.basename(script_realpath)
script_dir = os.path.dirname(script_realpath)
main_window_ui_file = os.path.join(script_dir, "main-window.ui")

# Empty Class+Object to contain widgets
class WidgetContainer:
    pass
widgets = WidgetContainer()

def load_widgets():
    # Initialize Builder
    widgets.builder = Gtk.Builder.new_from_file(main_window_ui_file)
    # Get Widgets from builder
    widgets.window_main = widgets.builder.get_object("window_main")
    widgets.dialog_error = widgets.builder.get_object("dialog_error")
    widgets.combobox = widgets.builder.get_object("combobox")
    widgets.button_quit = widgets.builder.get_object("button_quit")
    widgets.button_set_theme = widgets.builder.get_object("button_set_theme")

def call_set_theme(widget=None):
    selected_theme = widgets.combobox.get_active_text()
    if selected_theme:
        set_theme(theme=selected_theme, askpass="pkexec")
    else:
        widgets.dialog_error.present()

def on_activate(app):
    # Load Widgets
    load_widgets()

    # Add Theme List to combobox
    for theme in get_theme_list():
        widgets.combobox.append_text(theme)
    widgets.combobox.remove(0)

    # Connect Signals
    widgets.button_quit.connect("clicked", lambda x: widgets.window_main.close())
    widgets.button_set_theme.connect("clicked", call_set_theme)
    widgets.dialog_error.connect("response", lambda x,y: widgets.dialog_error.hide())

    # Add Window to app
    app.add_window(widgets.window_main)

    # Show Window
    widgets.window_main.present()


if __name__ == '__main__':
    app = Gtk.Application(application_id="org.gtk.gdm-settings")
    app.connect("activate", on_activate)
    app.run(sys.argv)
