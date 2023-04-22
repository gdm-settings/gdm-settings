'''A collection of general purpose and reusable widgets'''

from gettext import gettext as _

from gi.repository import Adw
from gi.repository import Gtk
from gi.repository import Pango
from gi.repository import Gio
from gi.repository import GObject
from gi.repository import GLib

from gdm_settings.utils import GProperty


class SwitchRow (Adw.ActionRow):
    __gtype_name__ = 'SwitchRow'

    enabled = GProperty(bool, default=False)

    def __init__ (self, **props):
        super().__init__(**props)

        switch = Gtk.Switch(valign=Gtk.Align.CENTER)
        switch.bind_property('active', self, 'enabled',
                             GObject.BindingFlags.SYNC_CREATE|GObject.BindingFlags.BIDIRECTIONAL)
        self.add_suffix(switch)
        self.set_activatable_widget(switch)


class FileChooserButton (Gtk.Button):
    __gtype_name__ = 'FileChooserButton'

    title = GProperty(str, default=_('Choose File'))
    filters = GProperty(Gio.ListModel)
    default_filter = GProperty(Gtk.FileFilter)


    def __init__ (self, **props):

        none_label = Gtk.Label(label=_('(None)'))

        self._file_image = Gtk.Image()
        self._file_label = Gtk.Label(ellipsize=Pango.EllipsizeMode.END, hexpand=True)

        file_box = Gtk.Box(orientation='horizontal', spacing=5)
        file_box.append(self._file_image)
        file_box.append(self._file_label)

        self._stack = Gtk.Stack(halign=Gtk.Align.START)
        self._stack.add_named(none_label, 'none_label')
        self._stack.add_named(file_box, 'file_box')
        self._stack.set_visible_child_name('none_label')

        main_box = Gtk.Box(orientation='horizontal', spacing=5)
        main_box.append(self._stack)
        main_box.append(Gtk.Separator(css_classes=['spacer'], halign=Gtk.Align.END, hexpand=True))
        main_box.append(Gtk.Image(icon_name='document-open-symbolic', halign=Gtk.Align.END))

        super().__init__(child=main_box, **props)

        self.file_dialog = Gtk.FileDialog(
            modal = True,
            title = self.title,
            filters = self.filters,
            default_filter = self.default_filter,
            accept_label = _('Choose'))


    @GProperty(str, default='')
    def filename (self):
        return self.file.get_path()

    @filename.setter
    def filename (self, value):
        self.file = Gio.File.new_for_path(value)


    @GProperty(Gio.File)
    def file (self):
        return self._file

    @file.setter
    def file (self, value):
        self._file = value
        self.notify('filename')
        self._update_ui()


    def _update_ui (self):
        if not self.file.get_path():
            self._stack.set_visible_child_name('none_label')
            return

        if self.file.query_exists(None):
            file_info = self.file.query_info('standard::*', 0, None)
            self._file_image.props.gicon = file_info.get_icon()
            self._file_label.props.label = file_info.get_display_name()
        else:
            self._file_image.props.icon_name = 'warning'
            self._file_label.props.label = self.file.get_basename()

        self._stack.set_visible_child_name('file_box')


    def do_clicked (self):
        self.file_dialog.set_initial_file(self.file),
        self.file_dialog.open(
            parent = self.get_root(),
            callback = self.file_dialog_open_finish_cb)

    def file_dialog_open_finish_cb(self, file_dialog, result):
        try:
            self.file = file_dialog.open_finish(result)
        except GLib.Error as err:
            if not err.matches(Gtk.dialog_error_quark(), Gtk.DialogError.DISMISSED):
                raise


class ImageChooserButton (FileChooserButton):
    __gtype_name__ = 'ImageChooserButton'

    def __init__ (self, **props):
        all_filters = Gio.ListStore()

        image_filter = Gtk.FileFilter(name=_('Images'))
        image_filter.add_mime_type('image/*')
        all_filters.append(image_filter)

        all_files_filter = Gtk.FileFilter(name=_('All Files'))
        all_files_filter.add_pattern('*')
        all_filters.append(all_files_filter)

        super().__init__(
            title = _('Choose Image'),
            filters = all_filters,
            default_filter = image_filter,
            **props)