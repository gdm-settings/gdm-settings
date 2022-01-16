#!/usr/bin/env python3
import gi, sys, os.path

gi.require_version("Adw", '1')

from gi.repository import Adw, Gtk, Gio, Gdk

from info import *
from functions import *

script_realpath = os.path.realpath(sys.argv[0])
script_basename = os.path.basename(script_realpath)
script_dir = os.path.dirname(script_realpath)

main_window_ui_file = os.path.join(script_dir, "main-window.ui")
app_menu_ui_file = os.path.join(script_dir, "app-menu.ui")
about_dialog_ui_file = os.path.join(script_dir, "about-dialog.ui")
theme_page_ui_file = os.path.join(script_dir, "theme.ui")
image_chooser_ui_file = os.path.join(script_dir, "image-chooser.ui")

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
    widgets.builder.add_from_file(image_chooser_ui_file)
    # Get Widgets from builder
    widgets.main_window = widgets.builder.get_object("main_window")
    widgets.app_menu = widgets.builder.get_object("app_menu")
    widgets.about_dialog = widgets.builder.get_object("about_dialog")
    widgets.page_stack = widgets.builder.get_object("stack")
    widgets.theme_page_box = widgets.builder.get_object("theme_page_box")
    widgets.theme_choice_comborow = widgets.builder.get_object("theme_choice_comborow")
    widgets.theme_page_apply_button = widgets.builder.get_object("theme_page_apply_button")
    widgets.bg_type_comborow = widgets.builder.get_object("bg_type_comborow")
    widgets.bg_type_list = widgets.builder.get_object("bg_type_list")
    widgets.bg_image_actionrow = widgets.builder.get_object("bg_image_actionrow")
    widgets.bg_image_button = widgets.builder.get_object("bg_image_button")
    widgets.bg_image_chooser = widgets.builder.get_object("bg_image_chooser")
    widgets.bg_color_actionrow = widgets.builder.get_object("bg_color_actionrow")
    widgets.bg_color_button = widgets.builder.get_object("bg_color_button")

def init_settings():
    widgets.settings = Gio.Settings(schema_id=application_id)

    # Load Theme Name
    set_theme = widgets.settings.get_string("theme")
    if set_theme:
        position = 0;
        for theme in widgets.theme_list_stringlist:
            if set_theme == theme.get_string():
                widgets.theme_choice_comborow.set_selected(position)
                break
            else:
                position += 1

    # Load Background Type
    set_bg_type = widgets.settings.get_string("background-type")
    position = 0
    for bg_type in widgets.bg_type_list:
        if bg_type.get_string() == set_bg_type:
            widgets.bg_type_comborow.set_selected(position)
            break
        else:
            position += 1

    # Load Background Color
    set_bg_color = widgets.settings.get_string("background-color")
    set_bg_color_rgba = Gdk.RGBA()
    Gdk.RGBA.parse(set_bg_color_rgba, set_bg_color)
    widgets.bg_color_button.set_rgba(set_bg_color_rgba)

    # Load Background Image
    set_bg_image = widgets.settings.get_string("background-image")
    if set_bg_image:
        widgets.bg_image_button.set_label(os.path.basename(set_bg_image))
        widgets.bg_image_chooser.set_file(Gio.File.new_for_path(set_bg_image))

def on_theme_page_apply_button_clicked(widget):
    # Background
    background_type = widgets.bg_type_comborow.get_selected_item().get_string()
    widgets.settings.set_string("background-type", background_type)
    if background_type == "Image":
        background_image = widgets.bg_image_chooser.get_file().get_path()
        widgets.settings.set_string("background-image", background_image)
    elif background_type == "Color":
        background_color = widgets.bg_color_button.get_rgba().to_string()
        widgets.settings.set_string("background-color", background_color)

    # Theme
    selected_theme = widgets.theme_choice_comborow.get_selected_item().get_string()
    set_theme(selected_theme)
    elevated_commands_list.run()
    widgets.settings.set_string("theme", selected_theme)

def on_bg_type_change():
    selected_type = widgets.bg_type_comborow.get_selected_item().get_string()
    if selected_type == "None":
        widgets.bg_image_actionrow.hide()
        widgets.bg_color_actionrow.hide()
    elif selected_type == "Image":
        widgets.bg_color_actionrow.hide()
        widgets.bg_image_actionrow.show()
    elif selected_type == "Color":
        widgets.bg_image_actionrow.hide()
        widgets.bg_color_actionrow.show()

def on_bg_image_button_clicked():
    widgets.bg_image_chooser.present()

def on_bg_image_chooser_response(widget, response):
    if response == Gtk.ResponseType.OK:
      image_file = widgets.bg_image_chooser.get_file()
      image_basename = image_file.get_basename()
      widgets.bg_image_button.set_label(image_basename)
    widgets.bg_image_chooser.hide()

def on_activate(app):
    # Load Widgets
    load_widgets()

    # Add Themes to List
    widgets.theme_list_stringlist = Gtk.StringList()
    for theme in get_theme_list():
        widgets.theme_list_stringlist.append(theme)
    widgets.theme_choice_comborow.set_model(widgets.theme_list_stringlist)

    # Connect Signals
    widgets.theme_page_apply_button.connect("clicked", on_theme_page_apply_button_clicked)
    widgets.bg_type_comborow.connect("notify::selected", lambda x,y: on_bg_type_change())
    widgets.bg_image_button.connect("clicked", lambda x: on_bg_image_button_clicked())
    widgets.bg_image_chooser.connect("response", on_bg_image_chooser_response)

    # Initialize GSettings
    init_settings()

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
    widgets.theme_page = widgets.page_stack.add(widgets.theme_page_box)

    # Set Page Properties
    widgets.theme_page.set_title("Theme")
    widgets.theme_page.set_icon_name(f"{application_id}-theme")

    # Set Title Main Window to Application Name
    widgets.main_window.set_title(application_name)

    # Add Window to app
    app.add_window(widgets.main_window)

    # Show Window
    widgets.main_window.present()

def on_shutdown(app):
    remove_temp_dir()

if __name__ == '__main__':
    app = Adw.Application(application_id=application_id)
    app.connect("activate", on_activate)
    app.connect("shutdown", on_shutdown)
    exit(app.run(sys.argv))
