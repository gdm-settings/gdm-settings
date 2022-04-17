'''The graphical user interface of the application'''

from sys import argv
from os import path

import gi
gi.require_version("Adw", '1')
from gi.repository import Adw, Gtk, Gio, Gdk

from .info import *
from .utils import find_file
from . import env
env.INTERFACE_TYPE = env.InterfaceType.Graphical

from . import settings_manager

# Empty Class+Object to contain widgets
class WidgetContainer:
    pass
widgets = WidgetContainer()

class App_Utils:
    def connect_signal(self, widget, signal, function):
        getattr(widgets, widget).connect(signal, function)

    def create_action(self, action_name, function):
        action = Gio.SimpleAction(name=action_name)
        action.connect("activate", function)
        self.add_action(action)
        setattr(widgets, action_name+'_action', action)

    def add_page_to_page_stack(self, title, name=None):
        name = name or title.lower().replace(" ", "_")
        page_content = getattr(widgets, name + '_page_content')
        page = widgets.page_stack.add_child(page_content)
        page.set_name(name)
        page.set_title(title)

    def set_comborow_setting(self, name):
        comborow = getattr(widgets, name+'_comborow')
        setattr(self.settings, name, comborow.get_selected_item().get_string())

    def set_switch_setting(self, name):
        switch = getattr(widgets, name.removeprefix('change_')+'_switch')
        setattr(self.settings, name, switch.get_active())

    def set_color_setting(self, name):
        color_button = getattr(widgets, name+'_button')
        setattr(self.settings, name, color_button.get_rgba().to_string())

    def set_file_chooser_setting(self, name):
        file_chooser = getattr(widgets, name+'_chooser')
        if file := file_chooser.get_file():
            setattr(self.settings, name, file.get_path())

    def set_font_setting(self, name):
        font_button = getattr(widgets, name.removeprefix('change_')+'_button')
        setattr(self.settings, name, font_button.get_font())

    def set_spinbutton_setting(self, name):
        spinbutton = getattr(widgets, name.removeprefix('change_')+'_spinbutton')
        setattr(self.settings, name, spinbutton.get_value())

class GDM_Settings(Adw.Application, App_Utils):
    def __init__(self):
        Adw.Application.__init__(self, application_id=application_id)
        self.connect("activate", self.on_activate)
        self.connect("shutdown", self.on_shutdown)

    ## Signal Handlers ##

    def on_activate(self, app):
        self.initialize_settings()
        self.get_widgets()
        self.bind_to_gsettings()
        self.set_widget_properties()
        self.load_theme_lists()
        self.connect_signals()
        self.load_settings_to_widgets()
        self.add_pages_to_page_stack()
        self.create_actions()
        self.keyboard_shortcuts()
        self.restore_window_state()
        self.add_window(widgets.main_window)
        widgets.main_window.present()

    def on_shutdown(self, app):
        self.save_window_state()
        self.settings.cleanup()

    def on_apply(self, widget):
        self.set_settings()

        # Apply
        if self.settings.apply_settings():
            widgets.main_toast_overlay.add_toast(widgets.apply_succeeded_toast)
        else:
            widgets.main_toast_overlay.add_toast(widgets.apply_failed_toast)

    def on_background_type_change(self, comborow, selection):
        selected = comborow.get_selected()
        if selected == 1:
            widgets.background_image_actionrow.show()
            widgets.background_color_actionrow.hide()
        elif selected == 2:
            widgets.background_color_actionrow.show()
            widgets.background_image_actionrow.hide()
        else:
            widgets.background_image_actionrow.hide()
            widgets.background_color_actionrow.hide()

    def on_background_image_chooser_response(self, widget, response):
        if response == Gtk.ResponseType.ACCEPT:
          image_file = widgets.background_image_chooser.get_file()
          image_basename = image_file.get_basename()
          widgets.background_image_button.set_label(image_basename)
        widgets.background_image_chooser.hide()

    def on_logo_chooser_response(self, widget, response):
        if response == Gtk.ResponseType.ACCEPT:
          image_file = widgets.logo_chooser.get_file()
          image_basename = image_file.get_basename()
          widgets.logo_button.set_label(image_basename)
        widgets.logo_chooser.hide()

    def on_apply_current_display_settings(self, button):
        toast = Adw.Toast(timeout=2, priority="high")
        if self.settings.apply_current_display_settings():
            toast.set_title(_("Applied current display settings"))
        else:
            toast.set_title(_("Failed to apply current display settings"))
        widgets.main_toast_overlay.add_toast(toast)

    def on_extract_shell_theme(self, button):
        toast = Adw.Toast(timeout=2, priority="high")
        additional_css = ""
        if widgets.include_top_bar_tweaks_switch.get_active():
            self.set_settings()
            additional_css = self.settings.get_setting_css()
        if settings_manager.gresource_utils.extract_default_theme(additional_css=additional_css):
            toast.set_title(_("Default shell theme extracted to '/usr/share/themes' as 'default-extracted'"))
        else:
            toast.set_title(_("Failed to extract default theme"))
        widgets.main_toast_overlay.add_toast(toast)

    #def on_extracted_theme_destination_chooser_response(self, widget, response):
    #    if response == Gtk.ResponseType.OK:
    #        toast = Adw.Toast(timeout=2, priority="high")
    #        widgets.main_toast_overlay.add_toast(toast)
    #        target_dir = widgets.extracted_theme_destination_chooser.get_file().get_path()
    #        if self.settings.extract_default_theme(target_dir):
    #            toast.set_title(_(f"Default theme saved as '{target_dir}/default-extracted'"))
    #        else:
    #            toast.set_title(_("Failed to extract default theme"))
    #    widgets.extracted_theme_destination_chooser.hide()

    ## Other methods ##

    def initialize_settings(self):
        self.settings = settings_manager.Settings()
        self.window_state = Gio.Settings(schema_id=f'{application_id}.window-state')

    def get_widgets(self):

        ui_files = [
            "main-window.ui",
            "appearance-page.ui",
            "fonts-page.ui",
            "display-page.ui",
            "sound-page.ui",
            "top-bar-page.ui",
            "pointing-page.ui",
            "misc-page.ui",
            "tools-page.ui",
        ]

        widget_list = [
            # Main Widgets
            "main_window",
            "paned",
            "app_menu",
            "about_dialog",
            "page_stack",
            "appearance_page_content",
            "fonts_page_content",
            "display_page_content",
            "sound_page_content",
            "top_bar_page_content",
            "pointing_page_content",
            "misc_page_content",
            "tools_page_content",
            "apply_button",
            "main_toast_overlay",
            "apply_failed_toast",
            "apply_succeeded_toast",
            "user_settings_imported_toast",
            "settings_reloaded_toast",

            # Widgets from Appearance page
            "shell_theme_comborow",
            "icon_theme_comborow",
            "cursor_theme_comborow",
            "background_type_comborow",
            "background_image_actionrow",
            "background_image_button",
            "background_image_chooser",
            "background_color_actionrow",
            "background_color_button",

            # Widgets from Fonts page
            "font_button",
            "antialiasing_comborow",
            "hinting_comborow",
            "scaling_factor_spinbutton",

            # Widgets from Top Bar page
            "disable_top_bar_arrows_switch",
            "disable_top_bar_rounded_corners_switch",
            "top_bar_text_color_switch",
            "top_bar_text_color_button",
            "top_bar_background_color_switch",
            "top_bar_background_color_button",
            "show_weekday_switch",
            "show_seconds_switch",
            "time_format_comborow",
            "show_battery_percentage_switch",

            # Widgets from Sound page
            "sound_theme_comborow",
            "event_sounds_switch",
            "feedback_sounds_switch",
            "over_amplification_switch",

            # Widgets from Mouse & Touchpad page
            "mouse_speed_scale",
            "pointer_acceleration_comborow",
            "mouse_inverse_scrolling_switch",
            "tap_to_click_switch",
            "natural_scrolling_switch",
            "two_finger_scrolling_switch",
            "disable_while_typing_switch",
            "touchpad_speed_scale",

            # Widgets from Display page
            "apply_current_display_settings_button",
            "night_light_enable_switch",
            "night_light_schedule_comborow",
            "night_light_start_box",
            "night_light_end_box",
            "night_light_start_hour_spinbutton",
            "night_light_start_minute_spinbutton",
            "night_light_end_hour_spinbutton",
            "night_light_end_minute_spinbutton",
            "night_light_color_temperature_scale",

            # Widgets from Misc page
            "enable_logo_switch",
            "logo_button",
            "enable_welcome_message_switch",
            "welcome_message_entry",
            "disable_restart_buttons_switch",
            "disable_user_list_switch",
            "logo_chooser",

            # Widgets from Tools page
            "include_top_bar_tweaks_switch",
            "extract_shell_theme_button",
            #"extracted_theme_destination_chooser",
        ]

        # Initialize Builder
        self.builder = Gtk.Builder()
        self.builder.set_translation_domain(project_name)

        # Load UI files
        for ui_file_name in ui_files:
            file = find_file(f"{project_name}/{ui_file_name}", locations=env.XDG_DATA_DIRS)
            self.builder.add_from_file(file)

        # Get Widgets from builder ####
        for widget in widget_list:
            setattr(widgets, widget, self.builder.get_object(widget))

    def bind_to_gsettings(self):
        tools_gsettings = Gio.Settings(schema_id=f"{application_id}.tools")
        tools_gsettings.bind('top-bar-tweaks', widgets.include_top_bar_tweaks_switch, 'active', Gio.SettingsBindFlags.DEFAULT)

    def set_widget_properties(self):
        # Main Window
        if build_type != 'release':
            widgets.main_window.add_css_class('devel')
        # Paned
        widgets.paned.set_shrink_start_child(False)
        widgets.paned.set_shrink_end_child(False)
        # About Dialog
        dev_mazhar_hussain = _("Mazhar Hussain") + " <mmazharhussainkgb1145@gmail.com>"
        widgets.about_dialog.set_authors([dev_mazhar_hussain])
        widgets.about_dialog.set_artists([dev_mazhar_hussain])
        widgets.about_dialog.set_documenters([dev_mazhar_hussain])
        # Translators: Do not translate this string. Put your info here in the form 'name <email>' including < and > but not qoutes.
        widgets.about_dialog.set_translator_credits(_("translator-credits"))
        # Font Scaling Factor SpinButton
        widgets.scaling_factor_spinbutton.set_range(0.5, 3)
        widgets.scaling_factor_spinbutton.set_increments(0.1,0.5)
        # Mouse Speed Scale
        widgets.mouse_speed_scale.set_range(-1, 1)
        # Touchpad Speed Scale
        widgets.touchpad_speed_scale.set_range(-1, 1)
        # Night Light Start Box
        widgets.night_light_start_box.set_direction(Gtk.TextDirection.LTR)
        # Night Light End Box
        widgets.night_light_end_box.set_direction(Gtk.TextDirection.LTR)
        # Night Light Start Hour SpinButton
        widgets.night_light_start_hour_spinbutton.set_range(0, 23)
        widgets.night_light_start_hour_spinbutton.set_increments(1,2)
        # Night Light Start Minute SpinButton
        widgets.night_light_start_minute_spinbutton.set_range(0, 59)
        widgets.night_light_start_minute_spinbutton.set_increments(1,5)
        # Night Light End Hour SpinButton
        widgets.night_light_end_hour_spinbutton.set_range(0, 23)
        widgets.night_light_end_hour_spinbutton.set_increments(1,2)
        # Night Light End Minute SpinButton
        widgets.night_light_end_minute_spinbutton.set_range(0, 59)
        widgets.night_light_end_minute_spinbutton.set_increments(1,5)
        # Night Light Temperature Scale
        widgets.night_light_color_temperature_scale.set_range(1700, 4700)

    def load_theme_lists(self):
        # Shell Themes
        widgets.shell_theme_list = Gtk.StringList()
        for theme in settings_manager.shell_themes:
            widgets.shell_theme_list.append(theme.name)
        widgets.shell_theme_comborow.set_model(widgets.shell_theme_list)
        # Icon Themes
        widgets.icon_theme_list = Gtk.StringList()
        for theme in settings_manager.icon_themes:
            widgets.icon_theme_list.append(theme.name)
        widgets.icon_theme_comborow.set_model(widgets.icon_theme_list)
        # Cursor Themes
        widgets.cursor_theme_list = Gtk.StringList()
        for theme in settings_manager.cursor_themes:
            widgets.cursor_theme_list.append(theme.name)
        widgets.cursor_theme_comborow.set_model(widgets.cursor_theme_list)
        # Sound Themes
        widgets.sound_theme_list = Gtk.StringList()
        for theme in settings_manager.sound_themes:
            widgets.sound_theme_list.append(theme.name)
        widgets.sound_theme_comborow.set_model(widgets.sound_theme_list)

    def connect_signals(self):
        self.connect_signal("apply_button", "clicked", self.on_apply)
        self.connect_signal("background_type_comborow", "notify::selected", self.on_background_type_change)
        self.connect_signal("background_image_button", "clicked",
                lambda x: widgets.background_image_chooser.show()
                )
        self.connect_signal("background_image_chooser", "response", self.on_background_image_chooser_response)
        self.connect_signal("logo_button", "clicked", lambda x: widgets.logo_chooser.show())
        self.connect_signal("logo_chooser", "response", self.on_logo_chooser_response)

        self.connect_signal("apply_current_display_settings_button", "clicked", self.on_apply_current_display_settings)
        self.connect_signal("extract_shell_theme_button", "clicked", self.on_extract_shell_theme)
        #self.connect_signal("extract_shell_theme_button", "clicked",
        #        lambda x: widgets.extracted_theme_destination_chooser.show()
        #        )
        #self.connect_signal("extracted_theme_destination_chooser", "response", self.on_extracted_theme_destination_chooser_response)

    def load_settings_to_widgets(self):
        #### Appearance ####
        # Shell Theme
        position = 0;
        for theme in widgets.shell_theme_list:
            if self.settings.shell_theme  == theme.get_string():
                widgets.shell_theme_comborow.set_selected(position)
                break
            else:
                position += 1

        # Icon Theme
        position = 0;
        for theme in widgets.icon_theme_list:
            if self.settings.icon_theme  == theme.get_string():
                widgets.icon_theme_comborow.set_selected(position)
                break
            else:
                position += 1

        # Cursor Theme
        position = 0;
        for theme in widgets.cursor_theme_list:
            if self.settings.cursor_theme  == theme.get_string():
                widgets.cursor_theme_comborow.set_selected(position)
                break
            else:
                position += 1

        # Background Type
        if self.settings.background_type == 'None':
            widgets.background_type_comborow.set_selected(0)
        elif self.settings.background_type == 'Image':
            widgets.background_type_comborow.set_selected(1)
        elif self.settings.background_type == 'Color':
            widgets.background_type_comborow.set_selected(2)

        # Background Color
        background_color_rgba = Gdk.RGBA()
        background_color_rgba.parse(self.settings.background_color)
        widgets.background_color_button.set_rgba(background_color_rgba)

        # Background Image
        if self.settings.background_image:
            widgets.background_image_button.set_label(path.basename(self.settings.background_image))
            widgets.background_image_chooser.set_file(Gio.File.new_for_path(self.settings.background_image))

        #### Fonts ####
        widgets.font_button.set_font(self.settings.font)
        if self.settings.antialiasing == 'grayscale':
            widgets.antialiasing_comborow.set_selected(0)
        elif self.settings.antialiasing == 'rgba':
            widgets.antialiasing_comborow.set_selected(1)
        elif self.settings.antialiasing == 'none':
            widgets.antialiasing_comborow.set_selected(3)
        if self.settings.hinting == 'full':
            widgets.hinting_comborow.set_selected(0)
        elif self.settings.hinting == 'medium':
            widgets.hinting_comborow.set_selected(1)
        elif self.settings.hinting == 'slight':
            widgets.hinting_comborow.set_selected(2)
        elif self.settings.hinting == 'none':
            widgets.hinting_comborow.set_selected(3)
        widgets.scaling_factor_spinbutton.set_value(self.settings.scaling_factor)

        #### Top Bar ####
        ## Tweaks ##
        # Arrows
        widgets.disable_top_bar_arrows_switch.set_active(self.settings.disable_top_bar_arrows)
        # Rounded Corners
        widgets.disable_top_bar_rounded_corners_switch.set_active(self.settings.disable_top_bar_rounded_corners)
        # Text Color
        widgets.top_bar_text_color_switch.set_active(self.settings.change_top_bar_text_color)
        top_bar_text_color_rgba = Gdk.RGBA()
        top_bar_text_color_rgba.parse(self.settings.top_bar_text_color)
        widgets.top_bar_text_color_button.set_rgba(top_bar_text_color_rgba)
        # Background Color
        widgets.top_bar_background_color_switch.set_active(self.settings.change_top_bar_background_color)
        top_bar_background_color_rgba = Gdk.RGBA()
        top_bar_background_color_rgba.parse(self.settings.top_bar_background_color)
        widgets.top_bar_background_color_button.set_rgba(top_bar_background_color_rgba)
        ## Time/Clock ##
        widgets.show_weekday_switch.set_active(self.settings.show_weekday)
        widgets.show_seconds_switch.set_active(self.settings.show_seconds)
        if self.settings.time_format == "12h":
            widgets.time_format_comborow.set_selected(0)
        else:
            widgets.time_format_comborow.set_selected(1)
        ## Power ##
        widgets.show_battery_percentage_switch.set_active(self.settings.show_battery_percentage)

        ##### Sound ####
        # Theme
        position = 0;
        for theme in widgets.sound_theme_list:
            if self.settings.sound_theme  == theme.get_string():
                widgets.sound_theme_comborow.set_selected(position)
                break
            else:
                position += 1

        widgets.event_sounds_switch.set_active(self.settings.event_sounds)
        widgets.feedback_sounds_switch.set_active(self.settings.feedback_sounds)
        widgets.over_amplification_switch.set_active(self.settings.over_amplification)

        #### Pointing ####
        ## Mouse ##
        widgets.mouse_inverse_scrolling_switch.set_active(self.settings.inverse_scrolling)
        if self.settings.pointer_acceleration == 'default':
            widgets.pointer_acceleration_comborow.set_selected(0)
        elif self.settings.pointer_acceleration == 'flat':
            widgets.pointer_acceleration_comborow.set_selected(1)
        elif self.settings.pointer_acceleration == 'adaptive':
            widgets.pointer_acceleration_comborow.set_selected(2)
        widgets.mouse_speed_scale.set_value(self.settings.mouse_speed)
        ## Touchpad ##
        widgets.tap_to_click_switch.set_active(self.settings.tap_to_click)
        widgets.natural_scrolling_switch.set_active(self.settings.natural_scrolling)
        widgets.two_finger_scrolling_switch.set_active(self.settings.two_finger_scrolling)
        widgets.disable_while_typing_switch.set_active(self.settings.disable_while_typing)
        widgets.touchpad_speed_scale.set_value(self.settings.touchpad_speed)

        #### Night Light ####
        widgets.night_light_enable_switch.set_active(self.settings.night_light_enabled)

        if self.settings.night_light_schedule_automatic:
            widgets.night_light_schedule_comborow.set_selected(0)
        else:
            widgets.night_light_schedule_comborow.set_selected(1)

        widgets.night_light_start_hour_spinbutton.set_value(self.settings.night_light_start_hour)
        widgets.night_light_start_minute_spinbutton.set_value(self.settings.night_light_start_minute)
        widgets.night_light_end_hour_spinbutton.set_value(self.settings.night_light_end_hour)
        widgets.night_light_end_minute_spinbutton.set_value(self.settings.night_light_end_minute)
        widgets.night_light_color_temperature_scale.set_value(self.settings.night_light_temperature)

        #### Misc ####
        widgets.disable_restart_buttons_switch.set_active(self.settings.disable_restart_buttons)
        widgets.disable_user_list_switch.set_active(self.settings.disable_user_list)
        widgets.enable_welcome_message_switch.set_active(self.settings.enable_welcome_message)
        widgets.welcome_message_entry.set_text(self.settings.welcome_message)
        widgets.enable_logo_switch.set_active(self.settings.enable_logo)
        if self.settings.logo:
            widgets.logo_button.set_label(path.basename(self.settings.logo))
            widgets.logo_chooser.set_file(Gio.File.new_for_path(self.settings.logo))

    def add_pages_to_page_stack(self):
        self.add_page_to_page_stack(_("Appearance"), 'appearance')
        self.add_page_to_page_stack(_("Fonts"), 'fonts')
        self.add_page_to_page_stack(_("Top Bar"), 'top_bar')
        self.add_page_to_page_stack(_("Sound"), 'sound')
        self.add_page_to_page_stack(_("Mouse & Touchpad"), 'pointing')
        self.add_page_to_page_stack(_("Display"), 'display')
        self.add_page_to_page_stack(_("Miscellaneous"), "misc")
        self.add_page_to_page_stack(_("Tools"), 'tools')

    def create_actions(self):
        self.create_action("quit", lambda x,y: self.quit())
        self.create_action("about", lambda x,y: widgets.about_dialog.present())
        self.create_action("import_user_settings", lambda x,y: self.import_user_settings())
        self.create_action("reload_settings", lambda x,y: self.reload_settings_to_widgets())
        self.create_action("reset_settings", lambda x,y: self.reset_settings())

    def keyboard_shortcuts(self):
        self.set_accels_for_action("app.quit", ["<Ctrl>q"])
        self.set_accels_for_action("app.reload_settings", ["<Ctrl>r", "F5"])

    def restore_window_state(self):
        # Window Size
        width = self.window_state.get_uint("width")
        height = self.window_state.get_uint("height")
        widgets.main_window.set_default_size(width, height)

        # Paned Position
        paned_position = self.window_state.get_uint("paned-position")
        widgets.paned.set_position(paned_position)

        # Last visited Page
        page_name = self.window_state.get_string("last-visited-page")
        widgets.page_stack.set_visible_child_name(page_name)

    def save_window_state(self):
        # Window Size
        width, height = widgets.main_window.get_default_size()
        self.window_state.set_uint("width", width)
        self.window_state.set_uint("height", height)

        # Paned Position
        paned_position = widgets.paned.get_position()
        self.window_state.set_uint("paned-position", paned_position)

        # Last visited Page
        page_name = widgets.page_stack.get_visible_child_name()
        self.window_state.set_string("last-visited-page", page_name)

    def reload_settings_to_widgets(self):
        self.settings.load_settings()
        self.load_settings_to_widgets()
        widgets.main_toast_overlay.add_toast(widgets.settings_reloaded_toast)

    def import_user_settings(self):
        if env.PACKAGE_TYPE is not env.PackageType.Flatpak:
            self.settings.load_user_settings()
            self.load_settings_to_widgets()
            widgets.main_toast_overlay.add_toast(widgets.user_settings_imported_toast)
        else:
            toast = Adw.Toast(timeout=2, priority="high")
            toast.set_title(_("Importing user settings is NOT supported in Flatpak version"))
            widgets.main_toast_overlay.add_toast(toast)

    def reset_settings(self):
        toast = Adw.Toast(timeout=2, priority="high",
                          title=_("Failed to reset settings"))

        if self.settings.reset_settings():
            self.load_settings_to_widgets()
            toast.set_title(_("Reset settings successfully"))

        widgets.main_toast_overlay.add_toast(toast)

    def set_settings(self):
        ## Appearance ##
        self.set_comborow_setting("shell_theme")
        self.set_comborow_setting("icon_theme")
        self.set_comborow_setting("cursor_theme")
        self.set_comborow_setting("background_type")
        self.set_file_chooser_setting("background_image")
        self.set_color_setting("background_color")

        ## Fonts ##
        self.set_font_setting("font")
        self.set_spinbutton_setting("scaling_factor")

        antialiasing = widgets.antialiasing_comborow.get_selected()
        if antialiasing == 0:
            self.settings.antialiasing = 'grayscale'
        elif antialiasing == 1:
            self.settings.antialiasing = 'rgba'
        elif antialiasing == 2:
            self.settings.antialiasing = 'none'

        hinting = widgets.hinting_comborow.get_selected()
        if hinting == 0:
            self.settings.hinting = 'full'
        elif hinting == 1:
            self.settings.hinting = 'medium'
        elif hinting == 2:
            self.settings.hinting = 'slight'
        elif hinting == 3:
            self.settings.hinting = 'none'

        ## Tob Bar ##
        # Tweaks
        self.set_switch_setting("disable_top_bar_arrows")
        self.set_switch_setting("disable_top_bar_rounded_corners")
        self.set_switch_setting("change_top_bar_text_color")
        self.set_switch_setting("change_top_bar_background_color")
        self.set_color_setting("top_bar_text_color")
        self.set_color_setting("top_bar_background_color")
        # Time/Clock
        self.settings.show_weekday   = widgets.show_weekday_switch.get_active()
        self.settings.show_seconds   = widgets.show_seconds_switch.get_active()
        self.settings.time_format    = "24h"
        if widgets.time_format_comborow.get_selected() == 0:
            self.settings.time_format = "12h"
        # Power
        self.settings.show_battery_percentage  = widgets.show_battery_percentage_switch.get_active()

        ## Sound ##
        self.settings.sound_theme    = widgets.sound_theme_comborow.get_selected_item().get_string()
        self.settings.feedback_sounds   = widgets.feedback_sounds_switch.get_active()
        self.settings.over_amplification   = widgets.over_amplification_switch.get_active()

        ## Pointing ##
        # Mouse
        self.settings.mouse_speed = widgets.mouse_speed_scale.get_value()
        self.settings.inverse_scrolling   = widgets.mouse_inverse_scrolling_switch.get_active()
        accel_profile = widgets.pointer_acceleration_comborow.get_selected()
        if accel_profile == 0:
            self.settings.pointer_acceleration = 'default'
        elif accel_profile == 1:
            self.settings.pointer_acceleration = 'flat'
        elif accel_profile == 2:
            self.settings.pointer_acceleration = 'adaptive'
        # Touchpad
        self.settings.tap_to_click   = widgets.tap_to_click_switch.get_active()
        self.settings.natural_scrolling   = widgets.natural_scrolling_switch.get_active()
        self.settings.two_finger_scrolling   = widgets.two_finger_scrolling_switch.get_active()
        self.settings.disable_while_typing   = widgets.disable_while_typing_switch.get_active()
        self.settings.touchpad_speed = widgets.touchpad_speed_scale.get_value()

        ## Night Light ##
        self.settings.night_light_enabled      = widgets.night_light_enable_switch.get_active()
        self.settings.night_light_temperature  = widgets.night_light_color_temperature_scale.get_value()
        self.settings.night_light_start_hour   = widgets.night_light_start_hour_spinbutton.get_value()
        self.settings.night_light_start_minute = widgets.night_light_start_minute_spinbutton.get_value()
        self.settings.night_light_end_hour     = widgets.night_light_end_hour_spinbutton.get_value()
        self.settings.night_light_end_minute   = widgets.night_light_end_minute_spinbutton.get_value()

        self.settings.night_light_schedule_automatic = False
        if widgets.night_light_schedule_comborow.get_selected() == 0:
            self.settings.night_light_schedule_automatic = True

        #### Misc ####
        self.set_switch_setting("disable_restart_buttons")
        self.set_switch_setting("disable_user_list")
        self.set_switch_setting("enable_logo")
        self.set_file_chooser_setting("logo")
        self.set_switch_setting("enable_welcome_message")
        self.settings.welcome_message = widgets.welcome_message_entry.get_text()

def main():
    app = GDM_Settings()
    return app.run(argv)

if __name__ == '__main__':
    main()
