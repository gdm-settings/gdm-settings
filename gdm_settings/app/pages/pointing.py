from gi.repository import Gtk

from gdm_settings.widgets import SwitchRow
from gdm_settings.settings import pointing_settings, mouse_settings, touchpad_settings

from .common import PageContent
from .pointing_utils.cursor import CursorSizeSelector


class PointingPageContent (PageContent):
    __gtype_name__ = 'PointingPageContent'

    def __init__ (self, window, **props):
        super().__init__(**props)

        self.window = window

        self.builder = Gtk.Builder.new_from_resource('/app/ui/pointing-page.ui')

        self.set_child(self.builder.get_object('content_box'))

        # General
        self.cursor_size_selector = self.builder.get_object('cursor_size_selector')
        # Mouse
        self.m_acceleration_comborow = self.builder.get_object('m_acceleration_comborow')
        self.m_natural_scrolling_row = self.builder.get_object('m_natural_scrolling_row')
        self.m_speed_scale = self.builder.get_object('m_speed_scale')
        # Touchpad
        self.t_tap_to_click_row = self.builder.get_object('t_tap_to_click_row')
        self.t_natural_scrolling_row = self.builder.get_object('t_natural_scrolling_row')
        self.t_two_finger_scrolling_row = self.builder.get_object('t_two_finger_scrolling_row')
        self.t_disable_while_typing_row = self.builder.get_object('t_disable_while_typing_row')
        self.t_speed_scale = self.builder.get_object('t_speed_scale')

        # Following properties are ignored when set in .ui files.
        # So, they need to be changed here.
        self.m_speed_scale.set_range(-1, 1)
        self.t_speed_scale.set_range(-1, 1)

        self.bind_to_gsettings()

    def bind_to_gsettings (self):
        # General
        pointing_settings.bind('cursor-size', self.cursor_size_selector, 'selected-size')
        # Mouse
        mouse_settings.bind_via_list('pointer-acceleration', self.m_acceleration_comborow, 'selected',
                                     ['default', 'flat', 'adaptive'])
        mouse_settings.bind('natural-scrolling', self.m_natural_scrolling_row, 'enabled')
        mouse_settings.bind('speed', self.m_speed_scale.props.adjustment, 'value')
        # Touchpad
        touchpad_settings.bind('tap-to-click', self.t_tap_to_click_row, 'enabled')
        touchpad_settings.bind('natural-scrolling', self.t_natural_scrolling_row, 'enabled')
        touchpad_settings.bind('two-finger-scrolling', self.t_two_finger_scrolling_row, 'enabled')
        touchpad_settings.bind('disable-while-typing', self.t_disable_while_typing_row, 'enabled')
        touchpad_settings.bind('speed', self.t_speed_scale.props.adjustment, 'value')
