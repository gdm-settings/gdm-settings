#!/usr/bin/env python3
import gi, sys, os.path

gi.require_version("Gtk", '4.0')
gi.require_version("Adw", '1')

from gi.repository import Gtk, Adw

from info import *
from functions import get_theme_list, set_theme, elevated_commands_list

script_realpath = os.path.realpath(sys.argv[0])
script_basename = os.path.basename(script_realpath)
script_dir = os.path.dirname(script_realpath)
main_window_ui_file = os.path.join(script_dir, "main-window.ui")
theme_page_ui_file = os.path.join(script_dir, "theme.ui")

# Empty Class+Object to contain widgets
class WidgetContainer:
    pass
widgets = WidgetContainer()

def load_widgets():
    # Initialize Builder
    widgets.builder = Gtk.Builder()
    # Load UI files
    widgets.builder.add_from_file(main_window_ui_file)
    widgets.builder.add_from_file(theme_page_ui_file)
    # Get Widgets from builder
    widgets.window_main = widgets.builder.get_object("window_main")
    widgets.stack_pages = widgets.builder.get_object("stack")
    widgets.box_page_theme = widgets.builder.get_object("theme_page")
    widgets.comborow = widgets.builder.get_object("comborow_theme_choice")
    widgets.button_quit = widgets.builder.get_object("button_quit")
    widgets.button_set_theme = widgets.builder.get_object("button_set_theme")

def call_set_theme(widget=None):
    selected_position = widgets.comborow.get_selected()
    selected_theme = widgets.stringlist_theme_list.get_string(selected_position)
    set_theme(selected_theme)
    elevated_commands_list.run()

def on_activate(app):
    # Load Widgets
    load_widgets()

    # Add Themes to List
    widgets.stringlist_theme_list = Gtk.StringList()
    for theme in get_theme_list():
        widgets.stringlist_theme_list.append(theme)
    widgets.comborow.set_model(widgets.stringlist_theme_list)

    # Connect Signals
    widgets.button_quit.connect("clicked", lambda x: widgets.window_main.close())
    widgets.button_set_theme.connect("clicked", call_set_theme)

    # Add Pages to Page Stack
    widgets.page_theme = widgets.stack_pages.add(widgets.box_page_theme)

    # Set Page Properties
    widgets.page_theme.set_title("Theme")
    widgets.page_theme.set_icon_name(f"{application_id}-theme")

    # Set Title Main Window to Application Name
    widgets.window_main.set_title(application_name)

    # Add Window to app
    app.add_window(widgets.window_main)

    # Show Window
    widgets.window_main.present()

if __name__ == '__main__':
    app = Adw.Application(application_id=application_id)
    app.connect("activate", on_activate)
    exit(app.run(sys.argv))
