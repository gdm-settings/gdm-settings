import os
from gi.repository import Adw, Gtk
from gi.repository import Gio, GObject
from gettext import gettext as _, pgettext as C_
from .info import data_dir, application_id, build_type
from .gr_utils import UbuntuGdmGresourceFile
from .utils import run_on_host
from .bind_utils import bind
from . import pages


construct = GObject.ParamFlags.CONSTRUCT
readwrite = GObject.ParamFlags.READWRITE

class TaskCounter(GObject.Object):
    '''A GObject that keeps a count of background tasks and updates widgets accordingly'''

    __gtype_name__ = 'TaskCounter'

    count = GObject.Property(type=int, default=0, flags=construct|readwrite)
    spinner = GObject.Property(type=Gtk.Spinner)

    def __init__ (self, **kwargs):
        super().__init__(**kwargs)

        self.widgets = []

        self.connect('notify::count', self.on_count_change)


    @staticmethod
    def on_count_change (self, prop):
        if self.count > 0:
            for widget in self.widgets:
                widget.set_sensitive(False)
            self.spinner.start()
        else:
            for widget in self.widgets:
                widget.set_sensitive(True)
            self.spinner.stop()

    def register (self, widget):
        self.widgets.append(widget)

    def inc (self):
        self.count += 1

    def dec (self):
        self.count -= 1


class GdmSettingsWindow (Adw.ApplicationWindow):
    __gtype_name__ = 'GdmSettingsWindow'

    def __init__ (self, application, **kwargs):
        super().__init__(**kwargs)

        self.application = application
        self.set_application(application)

        self.props.title = _('Login Manager Settings')

        self.builder = Gtk.Builder.new_from_file(os.path.join(data_dir, 'main-window.ui'))

        self.set_content(self.builder.get_object('content_box'))

        self.paned = self.builder.get_object('paned')
        self.stack = self.builder.get_object('stack')
        self.spinner = self.builder.get_object('spinner')
        self.apply_button = self.builder.get_object('apply_button')
        self.toast_overlay = self.builder.get_object('toast_overlay')

        self.task_counter = TaskCounter(spinner=self.spinner)

        self.task_counter.register(self.apply_button)
        self.apply_button.connect('clicked', self.on_apply)

        self.add_pages()
        self.bind_to_gsettings()

        if build_type != 'release':
            self.add_css_class('devel')

        # Following properties are ignored when set in .ui files.
        # So, they need to be changed here.
        self.paned.set_shrink_start_child(False)
        self.paned.set_shrink_end_child(False)

    def add_pages (self):

        def add_page(name, title, content):
            page = self.stack.add_named(content, name)
            page.set_title(title)

        add_page('appearance', _('Appearance'),       pages.AppearancePageContent(self))
        add_page('fonts',      _('Fonts'),            pages.FontsPageContent(self))
        add_page('top_bar',    _('Top Bar'),          pages.TopBarPageContent(self))
        add_page('sound',      _('Sound'),            pages.SoundPageContent(self))
        add_page('pointing',   _('Mouse & Touchpad'), pages.PointingPageContent(self))
        add_page('display',    _('Display'),          pages.DisplayPageContent(self))
        add_page('misc',       _('Miscellaneous'),    pages.MiscPageContent(self))
        add_page('tools',      _('Tools'),            pages.ToolsPageContent(self))

    def bind_to_gsettings (self):
        self.gsettings = Gio.Settings.new(f'{application_id}.window-state')

        bind(self.gsettings, 'width', self, 'default-width')
        bind(self.gsettings, 'height', self, 'default-height')
        bind(self.gsettings, 'paned-position', self.paned, 'position')
        bind(self.gsettings, 'last-visited-page', self.stack, 'visible-child-name')

    def on_apply (self, button):
        self.task_counter.inc()
        self.application.settings_manager.apply_settings_async(self.on_apply_finished)

    def on_apply_finished(self, settings_manager, result, user_data):
        status = settings_manager.apply_settings_finish(result)
        self.task_counter.dec()

        if status.success:
            message = _('Settings applied successfully')
        else:
            message = _('Failed to apply settings')

        toast = Adw.Toast(timeout=2, priority='high', title=message)
        self.toast_overlay.add_toast(toast)

        if UbuntuGdmGresourceFile or os.environ.get('XDG_CURRENT_DESKTOP') != 'GNOME':
            return

        message = _('The system may start to look weird/buggy untill you re-login or reboot.')

        dialog = Gtk.MessageDialog(
                         text = _('Log Out?'),
                        modal = True,
                      buttons = Gtk.ButtonsType.NONE,
                 message_type = Gtk.MessageType.QUESTION,
                transient_for = self,
               secondary_text = message,
         secondary_use_markup = True,
        )

        logout_button = Gtk.Button(label=_('Log Out'), css_classes=['destructive-action'])

        dialog.add_button(_('Cancel'), Gtk.ResponseType.CLOSE)
        dialog.add_action_widget(logout_button, Gtk.ResponseType.YES)
        dialog.connect('response', self.on_logout_dialog_response)
        dialog.present()

    def on_logout_dialog_response (self, dialog, response):
        if response == Gtk.ResponseType.YES:
            run_on_host(['gnome-session-quit', '--no-prompt'])
        else:
            dialog.close()
