import os
from gi.repository import Gtk
from ..info import data_dir
from ..settings import power_settings
from ..bind_utils import *
from .common import PageContent


class PowerPageContent (PageContent):
    __gtype_name__ = 'PowerPageContent'

    def __init__ (self, window, **kwargs):
        super().__init__(**kwargs)

        self.window = window

        self.builder = Gtk.Builder.new_from_file(os.path.join(data_dir, 'power-page.ui'))

        self.set_child(self.builder.get_object('content_box'))

        self.power_button_comborow = self.builder.get_object('power_button_comborow')
        self.auto_power_saver_switch = self.builder.get_object('auto_power_saver_switch')
        self.dim_screen_switch = self.builder.get_object('dim_screen_switch')
        self.screen_blank_switch = self.builder.get_object('screen_blank_switch')
        self.screen_blank_spinbutton = self.builder.get_object('screen_blank_spinbutton')
        self.suspend_on_battery_switch = self.builder.get_object('suspend_on_battery_switch')
        self.suspend_on_battery_spinbutton = self.builder.get_object('suspend_on_battery_spinbutton')
        self.suspend_on_ac_switch = self.builder.get_object('suspend_on_ac_switch')
        self.suspend_on_ac_spinbutton = self.builder.get_object('suspend_on_ac_spinbutton')

        self.bind_to_gsettings()

    def bind_to_gsettings (self):
        bind_comborow_by_list(self.power_button_comborow,
                power_settings, 'power-button-action', ['nothing', 'suspend', 'hibernate', 'interactive'])
        bind(power_settings, 'auto-power-saver', self.auto_power_saver_switch, 'active')
        bind(power_settings, 'dim-screen', self.dim_screen_switch, 'active')
        bind(power_settings, 'blank-screen', self.screen_blank_switch, 'active')
        bind(power_settings, 'idle-delay', self.screen_blank_spinbutton, 'value')
        bind(power_settings, 'suspend-on-battery', self.suspend_on_battery_switch, 'active')
        bind(power_settings, 'suspend-on-battery-delay', self.suspend_on_battery_spinbutton, 'value')
        bind(power_settings, 'suspend-on-ac', self.suspend_on_ac_switch, 'active')
        bind(power_settings, 'suspend-on-ac-delay', self.suspend_on_ac_spinbutton, 'value')
