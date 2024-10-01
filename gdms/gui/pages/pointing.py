from gi.repository import Gtk

from gdms.utils import GProperty
from gdms.settings import pointing_settings, mouse_settings, touchpad_settings

from .common import PageContent


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
        self.t_speed_scalerow= self.builder.get_object('t_speed_scalerow')
        self.t_enable_switch = self.builder.get_object('t_enable_switch')
        self.t_disable_on_external_mouse_row = self.builder.get_object('t_disable_on_external_mouse_row')

        self.t_enable_switch.connect("notify::active", self.on_switch_clicked);

        # Following properties are ignored when set in .ui files.
        # So, they need to be changed here.
        self.m_speed_scale.set_range(-1, 1)
        self.t_speed_scale.set_range(-1, 1)

        self.bind_to_gsettings()
        self.on_switch_clicked(self.t_enable_switch,None)


    def on_switch_clicked(self,widget, data):
        is_active = widget.get_active()

        # Perform actions based on the switch state
        if is_active:
            self.t_disable_on_external_mouse_row.set_sensitive(True)
            self.t_tap_to_click_row.set_sensitive(True)
            self.t_natural_scrolling_row.set_sensitive(True)
            self.t_two_finger_scrolling_row.set_sensitive(True)
            self.t_disable_while_typing_row.set_sensitive(True)
            self.t_speed_scalerow.set_sensitive(True)
            # Do something when the switch is active
        else:
            self.t_disable_on_external_mouse_row.set_sensitive(False)
            self.t_tap_to_click_row.set_sensitive(False)
            self.t_natural_scrolling_row.set_sensitive(False)
            self.t_two_finger_scrolling_row.set_sensitive(False)
            self.t_disable_while_typing_row.set_sensitive(False)
            self.t_speed_scalerow.set_sensitive(False)

    def bind_to_gsettings (self):
        # General
        pointing_settings.bind('cursor-size', self.cursor_size_selector, 'selected-size')
        # Mouse
        mouse_settings.bind_via_list('pointer-acceleration', self.m_acceleration_comborow, 'selected',
                                     ['default', 'flat', 'adaptive'])
        mouse_settings.bind('natural-scrolling', self.m_natural_scrolling_row, 'active')
        mouse_settings.bind('speed', self.m_speed_scale.props.adjustment, 'value')
        # Touchpad
        touchpad_settings.bind('tap-to-click', self.t_tap_to_click_row, 'active')
        touchpad_settings.bind('natural-scrolling', self.t_natural_scrolling_row, 'active')
        touchpad_settings.bind('two-finger-scrolling', self.t_two_finger_scrolling_row, 'active')
        touchpad_settings.bind('disable-while-typing', self.t_disable_while_typing_row, 'active')
        touchpad_settings.bind('speed', self.t_speed_scale.props.adjustment, 'value')
        touchpad_settings.bind('enable', self.t_enable_switch, 'active')
        touchpad_settings.bind('disable-on-external-mouse', self.t_disable_on_external_mouse_row, 'active')

@Gtk.Template(resource_path='/app/ui/pointing-page/cursor-size-button.ui')
class CursorSizeButton (Gtk.ToggleButton):
    __gtype_name__ = 'CursorSizeButton'

    cursor_size = GProperty(int, default=24, construct_only=True)
    size_name = GProperty(str)


@Gtk.Template(resource_path='/app/ui/pointing-page/cursor-size-selector.ui')
class CursorSizeSelector (Gtk.ListBoxRow, Gtk.Buildable):
    __gtype_name__ = 'CursorSizeSelector'
    box = Gtk.Template.Child()

    def __init__(self):
        super().__init__()

        self._item_dict = {}
        self._first_item = None
        self._selected_size = 0
        self._selected_name = ''

    @GProperty(int)
    def selected_size(self):
        return self._selected_size

    @selected_size.setter
    def selected_size(self, value):
        if self._selected_size == value:
            return

        if value not in self._item_dict:
            return

        self._selected_size = value
        btn = self._item_dict[value]
        btn.set_active(True)

        self._selected_name = btn.size_name
        self.notify('selected-name')

    @GProperty(str, writable=False)
    def selected_name(self):
        return self._selected_name

    def do_add_child(self, builder, child, _type):
        if not isinstance(child, CursorSizeButton):
            raise TypeError('Child is a ' + type(child) + '. Should be a CursorSizeButton instead')

        cursor_size = child.cursor_size
        if cursor_size in self._item_dict:
            raise ValueError('A CursorSizeButton with cursor-size of ' + cursor_size
                             + ' has already been added')

        self.box.append(child)
        child.connect('toggled', self.selection_changed_cb)
        self._item_dict[cursor_size] = child

        if self._first_item:
            child.set_group(self._first_item)
        else:
            self._first_item = child
            child.set_active(True)

    def selection_changed_cb(self, child):
        if not child.get_active() or child.cursor_size == self.selected_size:
            return

        self.selected_size = child.cursor_size
