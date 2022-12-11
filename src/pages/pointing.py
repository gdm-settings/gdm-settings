from gi.repository import Gtk
from ..utils import resource_path
from ..settings import mouse_settings, touchpad_settings
from ..bind_utils import *
from .common import PageContent
from .pointing_utils.cursor import CursorSizeSelector


class PointingPageContent (PageContent):
    __gtype_name__ = 'PointingPageContent'

    def __init__ (self, window, **kwargs):
        super().__init__(**kwargs)

        self.window = window

        self.builder = Gtk.Builder.new_from_resource(resource_path('ui/pointing-page.ui'))

        self.set_child(self.builder.get_object('content_box'))

        # Mouse
        self.m_acceleration_comborow = self.builder.get_object('m_acceleration_comborow')
        self.m_natural_scrolling_switch = self.builder.get_object('m_natural_scrolling_switch')
        self.m_speed_scale = self.builder.get_object('m_speed_scale')
        # Touchpad
        self.t_tap_to_click_switch = self.builder.get_object('t_tap_to_click_switch')
        self.t_natural_scrolling_switch = self.builder.get_object('t_natural_scrolling_switch')
        self.t_two_finger_scrolling_switch = self.builder.get_object('t_two_finger_scrolling_switch')
        self.t_disable_while_typing_switch = self.builder.get_object('t_disable_while_typing_switch')
        self.t_speed_scale = self.builder.get_object('t_speed_scale')

        # Following properties are ignored when set in .ui files.
        # So, they need to be changed here.
        self.m_speed_scale.set_range(-1, 1)
        self.t_speed_scale.set_range(-1, 1)

        self.bind_to_gsettings()

    def bind_to_gsettings (self):
        # Mouse
        bind_comborow_by_list(self.m_acceleration_comborow,
                mouse_settings, 'pointer-acceleration', ['default', 'flat', 'adaptive'])
        bind(mouse_settings, 'natural-scrolling', self.m_natural_scrolling_switch, 'active')
        bind(mouse_settings, 'speed', self.m_speed_scale.props.adjustment, 'value')
        # Touchpad
        bind(touchpad_settings, 'tap-to-click', self.t_tap_to_click_switch, 'active')
        bind(touchpad_settings, 'natural-scrolling', self.t_natural_scrolling_switch, 'active')
        bind(touchpad_settings, 'two-finger-scrolling', self.t_two_finger_scrolling_switch, 'active')
        bind(touchpad_settings, 'disable-while-typing', self.t_disable_while_typing_switch, 'active')
        bind(touchpad_settings, 'speed', self.t_speed_scale.props.adjustment, 'value')
