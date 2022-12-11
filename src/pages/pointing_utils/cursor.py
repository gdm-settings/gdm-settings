from gettext import pgettext as C_
from gi.repository import Adw, Gtk, GObject
from ...utils import resource_path
from ...settings import pointing_settings
from ...bind_utils import bind


@Gtk.Template(resource_path=resource_path('ui/pointing-page/cursor-image.ui'))
class CursorImage (Adw.Bin):
    __gtype_name__ = 'CursorImage'
    cursor_size = GObject.Property(type=int, default=24)


@Gtk.Template(resource_path=resource_path('ui/pointing-page/cursor-size-button.ui'))
class CursorSizeButton (Gtk.ToggleButton):
    __gtype_name__ = 'CursorSizeButton'
    cursor_size = GObject.Property(type=int, default=24, flags=GObject.ParamFlags.READWRITE|GObject.ParamFlags.CONSTRUCT_ONLY)


@Gtk.Template(resource_path=resource_path('ui/pointing-page/cursor-size-selector.ui'))
class CursorSizeSelector (Gtk.ListBoxRow):
    __gtype_name__ = 'CursorSizeSelector'
    box = Gtk.Template.Child()

    def __init__(self):
        super().__init__()

        self._item_dict = {}
        self._first_item = None
        self._selected_size = 0

        self.add_size(24)
        self.add_size(32)
        self.add_size(48)
        self.add_size(64)
        self.add_size(96)

        bind(pointing_settings, 'cursor-size', self, 'selected-size')

    @GObject.Property(type=int)
    def selected_size(self):
        return self._selected_size

    @selected_size.setter
    def selected_size(self, value):
        if self._selected_size == value:
            return

        if value not in self._item_dict:
            return

        self._selected_size = value
        self.notify('label-string')
        btn = self._item_dict[value]
        btn.set_active(True)

    @GObject.Property(type=str, flags=GObject.ParamFlags.READABLE)
    def label_string(self):
        match self.selected_size:
            case 24: return C_('Cursor Size', 'Default')
            case 32: return C_('Cursor Size', 'Medium')
            case 48: return C_('Cursor Size', 'Large')
            case 64: return C_('Cursor Size', 'Larger')
            case 96: return C_('Cursor Size', 'Largest')
            case __: return C_('Cursor Size', 'Non-Standard')

    def add_size(self, size):
        if size in self._item_dict:
            return

        child = CursorSizeButton(cursor_size=size)
        child.connect('toggled', self.selection_changed_cb)
        self._item_dict[size] = child
        self.box.append(child)

        if self._first_item:
            child.set_group(self._first_item)
        else:
            self._first_item = child
            child.set_active(True)

    def selection_changed_cb(self, child):
        if not child.get_active() or child.cursor_size == self.selected_size:
            return

        self.selected_size = child.cursor_size
