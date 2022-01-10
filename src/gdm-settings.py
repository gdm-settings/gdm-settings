#!/usr/bin/env python3
import gi, sys, os.path

gi.require_version("Adw", '1')

from gi.repository import Gtk, Adw

from info import *
from functions import get_theme_list, set_theme, elevated_commands_list

script_realpath = os.path.realpath(sys.argv[0])
script_basename = os.path.basename(script_realpath)
script_dir = os.path.dirname(script_realpath)

main_window_ui_file = os.path.join(script_dir, "main-window.ui")
app_menu_ui_file = os.path.join(script_dir, "app-menu.ui")
about_dialog_ui_file = os.path.join(script_dir, "about-dialog.ui")
theme_page_ui_file = os.path.join(script_dir, "theme.ui")

# Empty Class+Object to contain widgets
class WidgetContainer:
    pass
widgets = WidgetContainer()

def load_widgets():
    # Initialize Builder
    widgets.builder = Gtk.Builder()
    # Load UI files
    widgets.builder.add_from_file(app_menu_ui_file)
    widgets.builder.add_from_file(main_window_ui_file)
    widgets.builder.add_from_file(about_dialog_ui_file)
    widgets.builder.add_from_file(theme_page_ui_file)
    # Get Widgets from builder
    widgets.main_window = widgets.builder.get_object("main_window")
    widgets.app_menu = widgets.builder.get_object("app_menu")
    widgets.about_dialog = widgets.builder.get_object("about_dialog")
    widgets.stack_pages = widgets.builder.get_object("stack")
    widgets.box_page_theme = widgets.builder.get_object("theme_page")
    widgets.comborow = widgets.builder.get_object("comborow_theme_choice")
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
    widgets.button_set_theme.connect("clicked", call_set_theme)

    # Create Actions
    widgets.quit_action = Gio.SimpleAction(name="quit")
    widgets.about_action = Gio.SimpleAction(name="about")

    # Connect Signals
    widgets.quit_action.connect("activate", lambda x,y: app.quit())
    widgets.about_action.connect("activate", lambda x,y: widgets.about_dialog.present())

    # Add Actions to app
    app.add_action(widgets.quit_action)
    app.add_action(widgets.about_action)

    # Create Keyboard Shortcuts
    app.set_accels_for_action("quit", ["<Ctrl>Q"])

    # Add Pages to Page Stack
    widgets.page_theme = widgets.stack_pages.add(widgets.box_page_theme)

    # Set Page Properties
    widgets.page_theme.set_title("Theme")
    widgets.page_theme.set_icon_name(f"{application_id}-theme")

    # Set Title Main Window to Application Name
    widgets.main_window.set_title(application_name)

    # Add Window to app
    app.add_window(widgets.main_window)

    # Show Window
    widgets.main_window.present()

if __name__ == '__main__':
    app = Adw.Application(application_id=application_id)
    app.connect("activate", on_activate)
    exit(app.run(sys.argv))
