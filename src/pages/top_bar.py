import os
from gi.repository import Gtk
from ..utils import resource_path
from ..settings import top_bar_settings
from ..bind_utils import *
from .common import PageContent


class TopBarPageContent (PageContent):
    __gtype_name__ = 'TopBarPageContent'

    def __init__ (self, window, **kwargs):
        super().__init__(**kwargs)

        self.window = window

        self.builder = Gtk.Builder.new_from_resource(resource_path('ui/top-bar-page.ui'))

        self.set_child(self.builder.get_object('content_box'))

        self.text_color_switch = self.builder.get_object('text_color_switch')
        self.text_color_button = self.builder.get_object('text_color_button')
        self.background_color_switch = self.builder.get_object('background_color_switch')
        self.background_color_button = self.builder.get_object('background_color_button')
        self.disable_arrows_switch = self.builder.get_object('disable_arrows_switch')
        self.disable_rounded_corners_switch = self.builder.get_object('disable_rounded_corners_switch')
        self.show_weekday_switch = self.builder.get_object('show_weekday_switch')
        self.show_seconds_switch = self.builder.get_object('show_seconds_switch')
        self.time_format_comborow = self.builder.get_object('time_format_comborow')
        self.show_battery_percentage_switch = self.builder.get_object('show_battery_percentage_switch')

        self.bind_to_gsettings()

    def bind_to_gsettings (self):
        bind(top_bar_settings, 'disable-arrows', self.disable_arrows_switch, 'active')
        bind(top_bar_settings, 'disable-rounded-corners', self.disable_rounded_corners_switch, 'active')
        bind(top_bar_settings, 'change-text-color', self.text_color_switch, 'active')
        bind_colorbutton(self.text_color_button, top_bar_settings, 'text-color')
        bind(top_bar_settings, 'change-background-color', self.background_color_switch, 'active')
        bind_colorbutton(self.background_color_button, top_bar_settings, 'background-color')
        bind(top_bar_settings, 'show-weekday', self.show_weekday_switch, 'active')
        bind(top_bar_settings, 'show-seconds', self.show_seconds_switch, 'active')
        bind_comborow_by_list(self.time_format_comborow, top_bar_settings, 'time-format', ['12h', '24h'])
        bind(top_bar_settings, 'show-battery-percentage', self.show_battery_percentage_switch, 'active')
