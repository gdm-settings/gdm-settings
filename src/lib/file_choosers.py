from gettext import gettext as _, pgettext as C_

from gi.repository import Gtk
from gi.repository import Pango
from gi.repository import Gio
from gi.repository import GObject

from .misc import Property


__all__ = ['FileChooserButton', 'ImageChooserButton']


class FileChooserButton (Gtk.Button):
    __gtype_name__ = 'FileChooserButton'

    _freeze_prop_file = False
    _freeze_prop_filename = False
    _default_filter = Gtk.FileFilter(name=_('All Files'))
    _default_filter.add_pattern('*')

    title = Property(str, default=_('Choose File'))
    filter = Property(Gtk.FileFilter, default=_default_filter)
    filters = Property(Gio.ListModel, default=Gio.ListStore())


    def __init__ (self, **kwargs):

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

        super().__init__(**kwargs)

        self.set_child(main_box)


    @Property (str, default='')
    def filename (self):
        return self._filename

    @filename.setter
    def filename (self, value):
        self._filename = value
        self._freeze_prop_filename = True
        if not self._freeze_prop_file:
            self.file = Gio.File.new_for_path(value)
        self._freeze_prop_filename = False


    @Property (Gio.File)
    def file (self):
        return self._file

    @file.setter
    def file (self, value):
        self._file = value
        self._freeze_prop_file = True
        if not self._freeze_prop_filename:
            self.filename = value.get_path() or ''
        self._freeze_prop_file = False
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
        self._file_chooser = Gtk.FileChooserNative(
                                      modal = True,
                                     filter = self.filter,
                                      title = self.title,
                                     action = Gtk.FileChooserAction.OPEN,
                              transient_for = self.get_root(),
                               accept_label = _('Choose'),
                               cancel_label = _('Cancel'),
                )

        for filter in self.filters:
            self._file_chooser.add_filter(filter)

        self._file_chooser.connect('response', self._on_file_chooser_response)
        self._file_chooser.show()

    def _on_file_chooser_response(self, file_chooser, response):
        if response == Gtk.ResponseType.ACCEPT:
            self.file = file_chooser.get_file()
        file_chooser.destroy()


class ImageChooserButton (FileChooserButton):
    __gtype_name__ = 'ImageChooserButton'

    def __init__ (self, title=_('Choose Image'), **kwargs):
        super().__init__(title=title, **kwargs)

        self.filters = Gio.ListStore()

        image_filter = Gtk.FileFilter(name=_('Images'))
        image_filter.add_mime_type('image/*')
        self.filters.append(image_filter)

        all_filter = Gtk.FileFilter(name=_('All Files'))
        all_filter.add_pattern('*')
        self.filters.append(all_filter)

        self.filter = image_filter
