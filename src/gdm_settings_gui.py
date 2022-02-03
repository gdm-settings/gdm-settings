from sys import argv
from os import path

import gi
gi.require_version("Adw", '1')
from gi.repository import Adw, Gtk, Gio, Gdk

from . import settings_manager
from .info import *

# Empty Class+Object to contain widgets
class WidgetContainer:
    pass
widgets = WidgetContainer()

def get_widgets():
    # Initialize Builder
    widgets.builder = Gtk.Builder()

    # Load UI files
    main_window_ui_file = path.join(ui_dir, "main-window.ui")
    widgets.builder.add_from_file(main_window_ui_file)
    image_chooser_ui_file = path.join(ui_dir, "image-chooser.ui")
    widgets.builder.add_from_file(image_chooser_ui_file)
    appearance_page_ui_file = path.join(ui_dir, "appearance-page.ui")
    widgets.builder.add_from_file(appearance_page_ui_file)
    fonts_page_ui_file = path.join(ui_dir, "fonts-page.ui")
    widgets.builder.add_from_file(fonts_page_ui_file)
    night_light_page_ui_file = path.join(ui_dir, "night-light-page.ui")
    widgets.builder.add_from_file(night_light_page_ui_file)
    sound_page_ui_file = path.join(ui_dir, "sound-page.ui")
    widgets.builder.add_from_file(sound_page_ui_file)
    top_bar_page_ui_file = path.join(ui_dir, "top-bar-page.ui")
    widgets.builder.add_from_file(top_bar_page_ui_file)
    touchpad_page_ui_file = path.join(ui_dir, "touchpad-page.ui")
    widgets.builder.add_from_file(touchpad_page_ui_file)
    misc_page_ui_file = path.join(ui_dir, "misc-page.ui")
    widgets.builder.add_from_file(misc_page_ui_file)


    #### Get Widgets from builder ####

    # Main Widgets
    widgets.main_window = widgets.builder.get_object("main_window")
    widgets.paned = widgets.builder.get_object("paned")
    widgets.paned.set_shrink_start_child(False)
    widgets.paned.set_shrink_end_child(False)
    widgets.app_menu = widgets.builder.get_object("app_menu")
    widgets.about_dialog = widgets.builder.get_object("about_dialog")
    widgets.about_dialog.set_authors(["Mazhar Hussain <mmazharhussainkgb1145@gmail.com>"])
    widgets.about_dialog.set_artists(["Mazhar Hussain <mmazharhussainkgb1145@gmail.com>"])
    widgets.about_dialog.set_documenters(["Mazhar Hussain <mmazharhussainkgb1145@gmail.com>"])
    widgets.page_stack = widgets.builder.get_object("stack")
    widgets.appearance_page_content = widgets.builder.get_object("appearance_page_content")
    widgets.fonts_page_content = widgets.builder.get_object("fonts_page_content")
    widgets.night_light_page_content = widgets.builder.get_object("night_light_page_content")
    widgets.sound_page_content = widgets.builder.get_object("sound_page_content")
    widgets.top_bar_page_content = widgets.builder.get_object("top_bar_page_content")
    widgets.touchpad_page_content = widgets.builder.get_object("touchpad_page_content")
    widgets.misc_page_content = widgets.builder.get_object("misc_page_content")
    widgets.apply_button = widgets.builder.get_object("apply_button")
    widgets.main_toast_overlay = widgets.builder.get_object("main_toast_overlay")
    widgets.apply_failed_toast = widgets.builder.get_object("apply_failed_toast")
    widgets.apply_succeeded_toast = widgets.builder.get_object("apply_succeeded_toast")

    # Widgets from Appearance page
    widgets.shell_theme_comborow = widgets.builder.get_object("shell_theme_comborow")
    widgets.icon_theme_comborow = widgets.builder.get_object("icon_theme_comborow")
    widgets.cursor_theme_comborow = widgets.builder.get_object("cursor_theme_comborow")
    widgets.bg_type_comborow = widgets.builder.get_object("bg_type_comborow")
    widgets.bg_image_actionrow = widgets.builder.get_object("bg_image_actionrow")
    widgets.bg_image_button = widgets.builder.get_object("bg_image_button")
    widgets.image_chooser = widgets.builder.get_object("image_chooser")
    widgets.bg_color_actionrow = widgets.builder.get_object("bg_color_actionrow")
    widgets.bg_color_button = widgets.builder.get_object("bg_color_button")
    # Widgets from Fonts page
    widgets.font_button = widgets.builder.get_object("font_button")
    # Widgets from Top Bar page
    widgets.disable_top_bar_arrows_switch = widgets.builder.get_object("disable_top_bar_arrows_switch")
    widgets.disable_top_bar_rounded_corners_switch = widgets.builder.get_object("disable_top_bar_rounded_corners_switch")
    widgets.top_bar_text_color_switch = widgets.builder.get_object("top_bar_text_color_switch")
    widgets.top_bar_text_color_button = widgets.builder.get_object("top_bar_text_color_button")
    widgets.top_bar_background_color_switch = widgets.builder.get_object("top_bar_background_color_switch")
    widgets.top_bar_background_color_button = widgets.builder.get_object("top_bar_background_color_button")
    widgets.show_weekday_switch = widgets.builder.get_object("show_weekday_switch")
    widgets.show_seconds_switch = widgets.builder.get_object("show_seconds_switch")
    widgets.time_format_comborow = widgets.builder.get_object("time_format_comborow")
    widgets.show_battery_percentage_switch = widgets.builder.get_object("show_battery_percentage_switch")

    # Widgets from Sound page
    widgets.sound_theme_comborow = widgets.builder.get_object("sound_theme_comborow")
    # Widgets from Touchpad page
    widgets.tap_to_click_switch = widgets.builder.get_object("tap_to_click_switch")
    widgets.natural_scrolling_switch = widgets.builder.get_object("natural_scrolling_switch")
    widgets.touchpad_speed_scale = widgets.builder.get_object("touchpad_speed_scale")
    widgets.touchpad_speed_scale.set_range(-1, 1)
    # Widgets from Night Light page
    widgets.night_light_enable_switch = widgets.builder.get_object("night_light_enable_switch")
    widgets.night_light_schedule_comborow = widgets.builder.get_object("night_light_schedule_comborow")
    widgets.night_light_start_hour_spinbutton = widgets.builder.get_object("night_light_start_hour_spinbutton")
    widgets.night_light_start_hour_spinbutton.set_range(0, 23)
    widgets.night_light_start_hour_spinbutton.set_increments(1,2)
    widgets.night_light_start_minute_spinbutton = widgets.builder.get_object("night_light_start_minute_spinbutton")
    widgets.night_light_start_minute_spinbutton.set_range(0, 59)
    widgets.night_light_start_minute_spinbutton.set_increments(1,5)
    widgets.night_light_end_hour_spinbutton = widgets.builder.get_object("night_light_end_hour_spinbutton")
    widgets.night_light_end_hour_spinbutton.set_range(0, 23)
    widgets.night_light_end_hour_spinbutton.set_increments(1,2)
    widgets.night_light_end_minute_spinbutton = widgets.builder.get_object("night_light_end_minute_spinbutton")
    widgets.night_light_end_minute_spinbutton.set_range(0, 59)
    widgets.night_light_end_minute_spinbutton.set_increments(1,5)
    widgets.night_light_color_temperature_scale = widgets.builder.get_object("night_light_color_temperature_scale")
    widgets.night_light_color_temperature_scale.set_range(1700, 4700)

def add_string_lists_to_comborows():
    # Shell Themes
    widgets.shell_theme_list = Gtk.StringList()
    for theme in settings_manager.get_shell_theme_list():
        widgets.shell_theme_list.append(theme)
    widgets.shell_theme_comborow.set_model(widgets.shell_theme_list)
    # Icon Themes
    widgets.icon_theme_list = Gtk.StringList()
    for theme in settings_manager.get_icon_theme_list():
        widgets.icon_theme_list.append(theme)
    widgets.icon_theme_comborow.set_model(widgets.icon_theme_list)
    # Cursor Themes
    widgets.cursor_theme_list = Gtk.StringList()
    for theme in settings_manager.get_cursor_theme_list():
        widgets.cursor_theme_list.append(theme)
    widgets.cursor_theme_comborow.set_model(widgets.cursor_theme_list)
    # Sound Themes
    widgets.sound_theme_list = Gtk.StringList()
    for theme in settings_manager.get_sound_theme_list():
        widgets.sound_theme_list.append(theme)
    widgets.sound_theme_comborow.set_model(widgets.sound_theme_list)

def save_window_state():
    # Window Size
    width, height = widgets.main_window.get_default_size()
    widgets.window_state.set_uint("width", width)
    widgets.window_state.set_uint("height", height)

    # Paned Position
    paned_position = widgets.paned.get_position()
    widgets.window_state.set_uint("paned-position", paned_position)

    # Last visited Page
    page_name = widgets.page_stack.get_visible_child_name()
    widgets.window_state.set_string("last-visited-page", page_name)

def restore_window_state():
    # Window Size
    width = widgets.window_state.get_uint("width")
    height = widgets.window_state.get_uint("height")
    widgets.main_window.set_default_size(width, height)

    # Paned Position
    paned_position = widgets.window_state.get_uint("paned-position")
    widgets.paned.set_position(paned_position)

    # Last visited Page
    page_name = widgets.window_state.get_string("last-visited-page")
    widgets.page_stack.set_visible_child_name(page_name)

def init_settings():
    widgets.settings = settings_manager.Settings()
    widgets.window_state = Gio.Settings(schema_id=f'{application_id}.window-state')

def load_settings_to_widgets():
    settings = widgets.settings

    #### Get Settings ####
    # Interface
    icon_theme = settings.icon_theme
    cursor_theme = settings.cursor_theme
    sound_theme = settings.sound_theme
    show_battery_percentage = settings.show_battery_percentage
    show_weekday = settings.show_weekday
    time_format = settings.time_format
    # Touchpad
    tap_to_click = settings.tap_to_click
    touchpad_speed = settings.touchpad_speed
    # Night Light
    night_light_enabled = settings.night_light_enabled
    night_light_schedule_automatic = settings.night_light_schedule_automatic
    night_light_temperature = settings.night_light_temperature
    night_light_start_hour = settings.night_light_start_hour
    night_light_start_minute = settings.night_light_start_minute
    night_light_end_hour = settings.night_light_end_hour
    night_light_end_minute = settings.night_light_end_minute

    #### Load to Widgets ####
    # Icon Theme
    position = 0;
    for theme in widgets.icon_theme_list:
        if icon_theme  == theme.get_string():
            widgets.icon_theme_comborow.set_selected(position)
            break
        else:
            position += 1
    # Cursor Theme
    position = 0;
    for theme in widgets.cursor_theme_list:
        if cursor_theme  == theme.get_string():
            widgets.cursor_theme_comborow.set_selected(position)
            break
        else:
            position += 1
    # Sound Theme
    position = 0;
    for theme in widgets.sound_theme_list:
        if sound_theme  == theme.get_string():
            widgets.sound_theme_comborow.set_selected(position)
            break
        else:
            position += 1
    # Show Weekday
    widgets.show_weekday_switch.set_active(show_weekday)
    # Show Seconds
    widgets.show_seconds_switch.set_active(settings.show_seconds)
    # Clock Format
    if time_format == "12h":
        widgets.time_format_comborow.set_selected(0)
    else:
        widgets.time_format_comborow.set_selected(1)
    # Show Battery Percentage
    widgets.show_battery_percentage_switch.set_active(show_battery_percentage)
    # Touchpad
    widgets.tap_to_click_switch.set_active(tap_to_click)
    widgets.natural_scrolling_switch.set_active(settings.natural_scrolling)
    widgets.touchpad_speed_scale.set_value(touchpad_speed)
    # Night Light
    widgets.night_light_enable_switch.set_active(night_light_enabled)
    if night_light_schedule_automatic:
        widgets.night_light_schedule_comborow.set_selected(0)
    else:
        widgets.night_light_schedule_comborow.set_selected(1)
    widgets.night_light_start_hour_spinbutton.set_value(night_light_start_hour)
    widgets.night_light_start_minute_spinbutton.set_value(night_light_start_minute)
    widgets.night_light_end_hour_spinbutton.set_value(night_light_end_hour)
    widgets.night_light_end_minute_spinbutton.set_value(night_light_end_minute)
    widgets.night_light_color_temperature_scale.set_value(night_light_temperature)

    # Load Theme Name
    shell_theme = widgets.settings.shell_theme
    position = 0;
    for theme in widgets.shell_theme_list:
        if shell_theme  == theme.get_string():
            widgets.shell_theme_comborow.set_selected(position)
            break
        else:
            position += 1

    # Load Background Type
    if widgets.settings.background_type == 'None':
        widgets.bg_type_comborow.set_selected(0)
    elif widgets.settings.background_type == 'Image':
        widgets.bg_type_comborow.set_selected(1)
    elif widgets.settings.background_type == 'Color':
        widgets.bg_type_comborow.set_selected(2)

    # Load Background Color
    saved_bg_color = widgets.settings.background_color
    saved_bg_color_rgba = Gdk.RGBA()
    Gdk.RGBA.parse(saved_bg_color_rgba, saved_bg_color)
    widgets.bg_color_button.set_rgba(saved_bg_color_rgba)

    # Load Background Image
    saved_bg_image = widgets.settings.background_image
    if saved_bg_image:
        widgets.bg_image_button.set_label(path.basename(saved_bg_image))
        widgets.image_chooser.set_file(Gio.File.new_for_path(saved_bg_image))

    #### Load Theme Tweaks
    # Top Bar Arrows
    disable_top_bar_arrows = widgets.settings.disable_top_bar_arrows
    widgets.disable_top_bar_arrows_switch.set_active(disable_top_bar_arrows)
    # Top Bar Corners
    disable_top_bar_rounded_corners = widgets.settings.disable_top_bar_rounded_corners
    widgets.disable_top_bar_rounded_corners_switch.set_active(disable_top_bar_rounded_corners)
    # Top Bar Text Color
    change_top_bar_text_color = widgets.settings.change_top_bar_text_color
    widgets.top_bar_text_color_switch.set_active(change_top_bar_text_color)
    top_bar_text_color = widgets.settings.top_bar_text_color
    top_bar_text_color_rgba = Gdk.RGBA()
    top_bar_text_color_rgba.parse(top_bar_text_color)
    widgets.top_bar_text_color_button.set_rgba(top_bar_text_color_rgba)
    # Top Bar Background Color
    change_top_bar_background_color = widgets.settings.change_top_bar_background_color
    widgets.top_bar_background_color_switch.set_active(change_top_bar_background_color)
    top_bar_background_color = widgets.settings.top_bar_background_color
    top_bar_background_color_rgba = Gdk.RGBA()
    top_bar_background_color_rgba.parse(top_bar_background_color)
    widgets.top_bar_background_color_button.set_rgba(top_bar_background_color_rgba)

def reload_settings_to_widgets():
    widgets.settings.load_settings()
    load_settings_to_widgets()

def import_user_settings():
    widgets.settings.load_user_settings()
    load_settings_to_widgets()

def set_settings():
    settings = widgets.settings

    settings.icon_theme     = widgets.icon_theme_comborow.get_selected_item().get_string()
    settings.cursor_theme   = widgets.cursor_theme_comborow.get_selected_item().get_string()
    settings.sound_theme    = widgets.sound_theme_comborow.get_selected_item().get_string()
    settings.show_weekday   = widgets.show_weekday_switch.get_active()
    settings.show_seconds   = widgets.show_seconds_switch.get_active()
    settings.tap_to_click   = widgets.tap_to_click_switch.get_active()
    settings.touchpad_speed = widgets.touchpad_speed_scale.get_value()
    settings.natural_scrolling   = widgets.natural_scrolling_switch.get_active()
    settings.show_battery_percentage  = widgets.show_battery_percentage_switch.get_active()
    settings.night_light_enabled      = widgets.night_light_enable_switch.get_active()
    settings.night_light_temperature  = widgets.night_light_color_temperature_scale.get_value()

    settings.night_light_start_hour   = widgets.night_light_start_hour_spinbutton.get_value()
    settings.night_light_start_minute = widgets.night_light_start_minute_spinbutton.get_value()
    settings.night_light_end_hour     = widgets.night_light_end_hour_spinbutton.get_value()
    settings.night_light_end_minute   = widgets.night_light_end_minute_spinbutton.get_value()

    settings.time_format    = "24h"
    settings.night_light_schedule_automatic = True

    if widgets.time_format_comborow.get_selected() == 0:
        settings.time_format = "12h"

    if widgets.night_light_schedule_comborow.get_selected() == 1:
        settings.night_light_schedule_automatic = False

    # Theme
    settings.shell_theme = widgets.shell_theme_comborow.get_selected_item().get_string()
    # Background
    settings.background_type = widgets.bg_type_comborow.get_selected_item().get_string()
    if image_file := widgets.image_chooser.get_file():
        settings.background_image = image_file.get_path()
    settings.background_color = widgets.bg_color_button.get_rgba().to_string()
    # Top Bar Tweaks
    settings.disable_top_bar_arrows = widgets.disable_top_bar_arrows_switch.get_active()
    settings.disable_top_bar_rounded_corners = widgets.disable_top_bar_rounded_corners_switch.get_active()
    settings.change_top_bar_text_color = widgets.top_bar_text_color_switch.get_active()
    settings.top_bar_text_color = widgets.top_bar_text_color_button.get_rgba().to_string()
    settings.change_top_bar_background_color = widgets.top_bar_background_color_switch.get_active()
    settings.top_bar_background_color = widgets.top_bar_background_color_button.get_rgba().to_string()

def on_apply():
    set_settings()

    # Apply
    if widgets.settings.apply_settings():
        widgets.main_toast_overlay.add_toast(widgets.apply_succeeded_toast)
    else:
        widgets.main_toast_overlay.add_toast(widgets.apply_failed_toast)

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

def on_image_chooser_response(widget, response):
    if response == Gtk.ResponseType.OK:
      image_file = widgets.image_chooser.get_file()
      image_basename = image_file.get_basename()
      widgets.bg_image_button.set_label(image_basename)
    widgets.image_chooser.hide()

def on_activate(app):

    get_widgets()

    add_string_lists_to_comborows()

    # Connect Signals
    widgets.apply_button.connect("clicked", lambda x: on_apply())
    widgets.bg_type_comborow.connect("notify::selected", lambda x,y: on_bg_type_change())
    widgets.bg_image_button.connect("clicked", lambda x: widgets.image_chooser.present())
    widgets.image_chooser.connect("response", on_image_chooser_response)

    # Create Actions
    widgets.quit_action = Gio.SimpleAction(name="quit")
    widgets.about_action = Gio.SimpleAction(name="about")
    widgets.import_user_settings_action = Gio.SimpleAction(name="import_user_settings")
    widgets.reload_settings_action = Gio.SimpleAction(name="reload_settings")

    # Connect Signals
    widgets.quit_action.connect("activate", lambda x,y: app.quit())
    widgets.about_action.connect("activate", lambda x,y: widgets.about_dialog.present())
    widgets.import_user_settings_action.connect("activate", lambda x,y: import_user_settings())
    widgets.reload_settings_action.connect("activate", lambda x,y: reload_settings_to_widgets())

    # Add Actions to app
    app.add_action(widgets.quit_action)
    app.add_action(widgets.about_action)
    app.add_action(widgets.import_user_settings_action)
    app.add_action(widgets.reload_settings_action)

    # Create Keyboard Shortcuts
    app.set_accels_for_action("quit", ["<Ctrl>Q"])

    # Add Pages to Page Stack
    widgets.appearance_page = widgets.page_stack.add_child(widgets.appearance_page_content)
    widgets.fonts_page = widgets.page_stack.add_child(widgets.fonts_page_content)
    widgets.top_bar_page = widgets.page_stack.add_child(widgets.top_bar_page_content)
    widgets.sound_page = widgets.page_stack.add_child(widgets.sound_page_content)
    widgets.touchpad_page = widgets.page_stack.add_child(widgets.touchpad_page_content)
    widgets.night_light_page = widgets.page_stack.add_child(widgets.night_light_page_content)
    widgets.misc_page = widgets.page_stack.add_child(widgets.misc_page_content)

    # Set Appearance Page Properties
    widgets.appearance_page.set_name("appearance")
    widgets.appearance_page.set_title("Appearance")

    # Set Fonts Page Properties
    widgets.fonts_page.set_name("fonts")
    widgets.fonts_page.set_title("Fonts")

    # Set Night Light Page Properties
    widgets.night_light_page.set_name("night_light")
    widgets.night_light_page.set_title("Night Light")

    # Set Sound Page Properties
    widgets.sound_page.set_name("sound")
    widgets.sound_page.set_title("Sound")

    # Set Top Bar Page Properties
    widgets.top_bar_page.set_name("top_bar")
    widgets.top_bar_page.set_title("Top Bar")

    # Set Touchpad Page Properties
    widgets.touchpad_page.set_name("touchpad")
    widgets.touchpad_page.set_title("Touchpad")

    # Set Misc Page Properties
    widgets.misc_page.set_name("misc")
    widgets.misc_page.set_title("Miscellaneous")

    # Initialize and Load Settings
    init_settings()
    load_settings_to_widgets()

    # Restore window state
    restore_window_state()

    # Set Title Main Window to Application Name
    widgets.main_window.set_title(application_name)

    # Add Window to app
    app.add_window(widgets.main_window)

    # Show Window
    widgets.main_window.present()

def on_shutdown(app):
    save_window_state()
    widgets.settings.cleanup()

def main():
    app = Adw.Application(application_id=application_id)
    app.connect("activate", on_activate)
    app.connect("shutdown", on_shutdown)
    exit(app.run(argv))

if __name__ == '__main__':
    main()
