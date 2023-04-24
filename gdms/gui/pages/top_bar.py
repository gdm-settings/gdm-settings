from gi.repository import Gtk

from gdms.gui.widgets import SwitchRow
from gdms.settings import accessibility_settings, top_bar_settings

from .common import PageContent


class TopBarPageContent (PageContent):
    __gtype_name__ = 'TopBarPageContent'

    def __init__ (self, window, **props):
        super().__init__(**props)

        self.window = window

        self.builder = Gtk.Builder.new_from_resource('/app/ui/top-bar-page.ui')

        self.set_child(self.builder.get_object('content_box'))

        self.text_color_switch = self.builder.get_object('text_color_switch')
        self.text_color_button = self.builder.get_object('text_color_button')
        self.background_color_switch = self.builder.get_object('background_color_switch')
        self.background_color_button = self.builder.get_object('background_color_button')
        self.disable_arrows_row = self.builder.get_object('disable_arrows_row')
        self.disable_rounded_corners_row = self.builder.get_object('disable_rounded_corners_row')
        self.accessibilty_menu_row = self.builder.get_object('accessibilty_menu_row')
        self.show_weekday_row = self.builder.get_object('show_weekday_row')
        self.show_seconds_row = self.builder.get_object('show_seconds_row')
        self.time_format_comborow = self.builder.get_object('time_format_comborow')
        self.show_battery_percentage_row = self.builder.get_object('show_battery_percentage_row')

        self.bind_to_gsettings()

    def bind_to_gsettings (self):
        top_bar_settings.bind('disable-arrows', self.disable_arrows_row, 'enabled')
        top_bar_settings.bind('disable-rounded-corners', self.disable_rounded_corners_row, 'enabled')
        top_bar_settings.bind('change-text-color', self.text_color_switch, 'active')
        top_bar_settings.bind_to_colorbutton('text-color', self.text_color_button)
        top_bar_settings.bind('change-background-color', self.background_color_switch, 'active')
        top_bar_settings.bind_to_colorbutton('background-color', self.background_color_button)
        accessibility_settings.bind('always-show-accessibility-menu',
                                    self.accessibilty_menu_row, 'enabled')
        top_bar_settings.bind('show-weekday', self.show_weekday_row, 'enabled')
        top_bar_settings.bind('show-seconds', self.show_seconds_row, 'enabled')
        top_bar_settings.bind_via_list('time-format', self.time_format_comborow, 'selected', ['12h', '24h'])
        top_bar_settings.bind('show-battery-percentage', self.show_battery_percentage_row, 'enabled')
