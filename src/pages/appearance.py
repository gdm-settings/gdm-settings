import os
from gi.repository import Gtk
from ..utils import resource_path
from ..enums import BackgroundType
from ..settings import appearance_settings
from ..common_widgets import ImageChooserButton
from ..theme_lists import shell_themes, icon_themes, cursor_themes
from ..bind_utils import *
from .common import PageContent


class AppearancePageContent (PageContent):
    __gtype_name__ = 'AppearancePageContent'

    def __init__ (self, window, **kwargs):
        super().__init__(**kwargs)

        self.window = window

        self.builder = Gtk.Builder.new_from_resource(resource_path('ui/appearance-page.ui'))

        self.set_child(self.builder.get_object('content_box'))

        self.shell_theme_comborow = self.builder.get_object('shell_theme_comborow')
        self.icon_theme_comborow = self.builder.get_object('icon_theme_comborow')
        self.cursor_theme_comborow = self.builder.get_object('cursor_theme_comborow')
        
        self.background_type_comborow = self.builder.get_object('background_type_comborow')
        self.background_image_actionrow = self.builder.get_object('background_image_actionrow')
        self.background_color_actionrow = self.builder.get_object('background_color_actionrow')
        self.background_color_button = self.builder.get_object('background_color_button')

        # Add background image button
        self.background_image_button = ImageChooserButton(valign='center')
        self.background_image_actionrow.add_suffix(self.background_image_button)
        self.background_image_actionrow.set_activatable_widget(self.background_image_button)

        self.background_type_comborow.connect('notify::selected', self.on_background_type_changed)

        self.load_theme_lists()
        self.bind_to_gsettings()


    def on_background_type_changed (self, comborow, prop):
        background_type = BackgroundType(comborow.get_selected())
        if background_type is BackgroundType.image:
            self.background_image_actionrow.set_visible(True)
            self.background_color_actionrow.set_visible(False)
        elif background_type is BackgroundType.color:
            self.background_image_actionrow.set_visible(False)
            self.background_color_actionrow.set_visible(True)
        else:
            self.background_image_actionrow.set_visible(False)
            self.background_color_actionrow.set_visible(False)


    def load_theme_lists(self):
        # Shell Themes
        shell_theme_list = Gtk.StringList()
        for theme_name in shell_themes.names:
            shell_theme_list.append(theme_name)
        self.shell_theme_comborow.set_model(shell_theme_list)

        # Icon Themes
        icon_theme_list = Gtk.StringList()
        for theme_name in icon_themes.names:
            icon_theme_list.append(theme_name)
        self.icon_theme_comborow.set_model(icon_theme_list)

        # Cursor Themes
        cursor_theme_list = Gtk.StringList()
        for theme_name in cursor_themes.names:
            cursor_theme_list.append(theme_name)
        self.cursor_theme_comborow.set_model(cursor_theme_list)

    def bind_to_gsettings (self):
        bind_comborow(self.shell_theme_comborow, appearance_settings, 'shell-theme')
        bind_comborow(self.icon_theme_comborow, appearance_settings, 'icon-theme')
        bind_comborow(self.cursor_theme_comborow, appearance_settings, 'cursor-theme')
        bind_comborow_by_enum(self.background_type_comborow,
                appearance_settings, 'background-type', BackgroundType)
        bind(appearance_settings, 'background-image', self.background_image_button, 'filename')
        bind_colorbutton(self.background_color_button, appearance_settings, 'background-color')
