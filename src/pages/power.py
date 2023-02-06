import os

from gi.repository import Gtk

from ..lib import SwitchRow
from ..utils import resource_path
from ..settings import power_settings
from .common import PageContent


class PowerPageContent (PageContent):
    __gtype_name__ = 'PowerPageContent'

    def __init__ (self, window, **kwargs):
        super().__init__(**kwargs)

        self.window = window

        self.builder = Gtk.Builder.new_from_resource(resource_path('ui/power-page.ui'))

        self.set_child(self.builder.get_object('content_box'))

        self.power_button_comborow = self.builder.get_object('power_button_comborow')
        self.auto_power_saver_row = self.builder.get_object('auto_power_saver_row')
        self.dim_screen_row = self.builder.get_object('dim_screen_row')
        self.screen_blank_switch = self.builder.get_object('screen_blank_switch')
        self.screen_blank_spinbutton = self.builder.get_object('screen_blank_spinbutton')
        self.suspend_on_battery_switch = self.builder.get_object('suspend_on_battery_switch')
        self.suspend_on_battery_spinbutton = self.builder.get_object('suspend_on_battery_spinbutton')
        self.suspend_on_ac_switch = self.builder.get_object('suspend_on_ac_switch')
        self.suspend_on_ac_spinbutton = self.builder.get_object('suspend_on_ac_spinbutton')

        self.bind_to_gsettings()

    def bind_to_gsettings (self):
        power_settings.bind_via_list('power-button-action', self.power_button_comborow, 'selected',
                                     ['nothing', 'suspend', 'hibernate', 'interactive'])
        power_settings.bind('auto-power-saver', self.auto_power_saver_row, 'enabled')
        power_settings.bind('dim-screen', self.dim_screen_row, 'enabled')
        power_settings.bind('blank-screen', self.screen_blank_switch, 'active')
        power_settings.bind('idle-delay', self.screen_blank_spinbutton, 'value')
        power_settings.bind('suspend-on-battery', self.suspend_on_battery_switch, 'active')
        power_settings.bind('suspend-on-battery-delay', self.suspend_on_battery_spinbutton, 'value')
        power_settings.bind('suspend-on-ac', self.suspend_on_ac_switch, 'active')
        power_settings.bind('suspend-on-ac-delay', self.suspend_on_ac_spinbutton, 'value')
