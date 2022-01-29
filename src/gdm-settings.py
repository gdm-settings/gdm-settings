#!/usr/bin/env python3
import gi, sys, os.path

gi.require_version("Adw", '1')
from gi.repository import Adw, Gtk, Gio, Gdk

from info import *
from functions import *
from theme_settings_manager import *

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
    widgets.theme_page_content = widgets.builder.get_object("theme_page_content")
    widgets.theme_choice_comborow = widgets.builder.get_object("theme_choice_comborow")
    widgets.apply_button = widgets.builder.get_object("apply_button")
    widgets.bg_type_comborow = widgets.builder.get_object("bg_type_comborow")
    widgets.bg_type_list = widgets.builder.get_object("bg_type_list")
    widgets.bg_image_actionrow = widgets.builder.get_object("bg_image_actionrow")
    widgets.bg_image_button = widgets.builder.get_object("bg_image_button")
    widgets.bg_image_chooser = widgets.builder.get_object("bg_image_chooser")
    widgets.bg_color_actionrow = widgets.builder.get_object("bg_color_actionrow")
    widgets.bg_color_button = widgets.builder.get_object("bg_color_button")
    widgets.disable_top_bar_arrows_switch = widgets.builder.get_object("disable_top_bar_arrows_switch")
    widgets.change_top_bar_text_color_switch = widgets.builder.get_object("change_top_bar_text_color_switch")
    widgets.top_bar_text_color_button = widgets.builder.get_object("top_bar_text_color_button")
    #widgets.top_bar_transparency_scale = widgets.builder.get_object("top_bar_transparency_scale")
    #widgets.top_bar_transparency_scale.set_range(0, 1)

def init_settings():
    widgets.theme_settings = ThemeSettings()

    # Load Theme Name
    saved_theme = widgets.theme_settings.theme
    position = 0;
    for theme in widgets.theme_list_stringlist:
        if saved_theme  == theme.get_string():
            widgets.theme_choice_comborow.set_selected(position)
            break
        else:
            position += 1

    # Load Background Type
    position = 0
    saved_bg_type = widgets.theme_settings.background_type
    for bg_type in widgets.bg_type_list:
        if bg_type.get_string() == saved_bg_type:
            widgets.bg_type_comborow.set_selected(position)
            break
        else:
            position += 1

    # Load Background Color
    saved_bg_color = widgets.theme_settings.background_color
    saved_bg_color_rgba = Gdk.RGBA()
    Gdk.RGBA.parse(saved_bg_color_rgba, saved_bg_color)
    widgets.bg_color_button.set_rgba(saved_bg_color_rgba)

    # Load Background Image
    saved_bg_image = widgets.theme_settings.background_image
    if saved_bg_image:
        widgets.bg_image_button.set_label(os.path.basename(saved_bg_image))
        widgets.bg_image_chooser.set_file(Gio.File.new_for_path(saved_bg_image))

    #### Load Theme Tweaks
    # Top Bar Arrows
    disable_top_bar_arrows = widgets.theme_settings.disable_top_bar_arrows
    widgets.disable_top_bar_arrows_switch.set_active(disable_top_bar_arrows)
    # Top Bar Text Color
    change_top_bar_text_color = widgets.theme_settings.change_top_bar_text_color
    widgets.change_top_bar_text_color_switch.set_active(change_top_bar_text_color)
    top_bar_text_color = widgets.theme_settings.top_bar_text_color
    top_bar_text_color_rgba = Gdk.RGBA()
    top_bar_text_color_rgba.parse(top_bar_text_color)
    widgets.top_bar_text_color_button.set_rgba(top_bar_text_color_rgba)

def on_apply(widget):
    # Background
    widgets.theme_settings.background_type = widgets.bg_type_comborow.get_selected_item().get_string()
    widgets.theme_settings.background_image = widgets.bg_image_chooser.get_file().get_path()
    widgets.theme_settings.background_color = widgets.bg_color_button.get_rgba().to_string()
    # Theme
    widgets.theme_settings.theme = widgets.theme_choice_comborow.get_selected_item().get_string()
    # Theme Tweaks
    widgets.theme_settings.disable_top_bar_arrows = widgets.disable_top_bar_arrows_switch.get_active()
    widgets.theme_settings.change_top_bar_text_color = widgets.change_top_bar_text_color_switch.get_active()
    widgets.theme_settings.top_bar_text_color = widgets.top_bar_text_color_button.get_rgba().to_string()
    # Apply
    widgets.theme_settings.apply_settings()

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
    widgets.apply_button.connect("clicked", on_apply)
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
    widgets.theme_page = widgets.page_stack.add(widgets.theme_page_content)

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
    shutil.rmtree(path=TempDir, ignore_errors=True)

if __name__ == '__main__':
    app = Adw.Application(application_id=application_id)
    app.connect("activate", on_activate)
    app.connect("shutdown", on_shutdown)
    exit(app.run(sys.argv))
