import os
from gi.repository import Adw, Gtk
from gettext import gettext as _, pgettext as C_
from ..info import data_dir
from ..settings import night_light_settings as nl_settings
from ..bind_utils import *
from .common import PageContent


class DisplayPageContent (PageContent):
    __gtype_name__ = 'DisplayPageContent'

    def __init__ (self, window, **kwargs):
        super().__init__(**kwargs)

        self.window = window

        self.builder = Gtk.Builder.new_from_file(os.path.join(data_dir, 'display-page.ui'))

        self.set_child(self.builder.get_object('content_box'))

        self.apply_display_settings_button = self.builder.get_object('apply_display_settings_button')
        self.apply_display_settings_button.connect('clicked', self.on_apply_display_settings)

        self.nl_enable_switch = self.builder.get_object('nl_enable_switch')
        self.nl_schedule_comborow = self.builder.get_object('nl_schedule_comborow')
        self.nl_start_box = self.builder.get_object('nl_start_box')
        self.nl_start_hour_spinbutton = self.builder.get_object('nl_start_hour_spinbutton')
        self.nl_start_minute_spinbutton = self.builder.get_object('nl_start_minute_spinbutton')
        self.nl_end_box = self.builder.get_object('nl_end_box')
        self.nl_end_hour_spinbutton = self.builder.get_object('nl_end_hour_spinbutton')
        self.nl_end_minute_spinbutton = self.builder.get_object('nl_end_minute_spinbutton')
        self.nl_temperature_scale = self.builder.get_object('nl_temperature_scale')

        # Following properties are ignored when set in .ui files.
        # So, they need to be changed here.
        self.nl_start_box.set_direction(Gtk.TextDirection.LTR)
        self.nl_end_box.set_direction(Gtk.TextDirection.LTR)
        self.nl_start_hour_spinbutton.set_range(0, 23)
        self.nl_start_hour_spinbutton.set_increments(1,2)
        self.nl_start_minute_spinbutton.set_range(0, 59)
        self.nl_start_minute_spinbutton.set_increments(1,5)
        self.nl_end_hour_spinbutton.set_range(0, 23)
        self.nl_end_hour_spinbutton.set_increments(1,2)
        self.nl_end_minute_spinbutton.set_range(0, 59)
        self.nl_end_minute_spinbutton.set_increments(1,5)
        self.nl_temperature_scale.set_range(1700, 4700)

        self.nl_schedule_comborow.connect('notify::selected', self.update_time_row_sensitivity)

        self.bind_to_gsettings()

    def update_time_row_sensitivity (self, comborow, prop):
        selected = comborow.get_selected()
        self.nl_start_box.set_sensitive(bool(selected))
        self.nl_end_box.set_sensitive(bool(selected))

    def bind_to_gsettings (self):
        bind(nl_settings, 'enabled', self.nl_enable_switch, 'active')
        bind_comborow_by_list(self.nl_schedule_comborow, nl_settings, 'schedule-automatic', [True, False])
        bind(nl_settings, 'start-hour', self.nl_start_hour_spinbutton, 'value')
        bind(nl_settings, 'start-minute', self.nl_start_minute_spinbutton, 'value')
        bind(nl_settings, 'end-hour', self.nl_end_hour_spinbutton, 'value')
        bind(nl_settings, 'end-minute', self.nl_end_minute_spinbutton, 'value')
        bind(nl_settings, 'temperature', self.nl_temperature_scale.props.adjustment, 'value')

    def on_apply_display_settings (self, button):
        try:
            status = self.window.application.settings_manager.apply_user_display_settings()
            if status.success:
                message = _("Applied current display settings")
            else:
                message = _("Failed to apply current display settings")
            toast = Adw.Toast(timeout=2, priority="high", title=message)
            self.window.toast_overlay.add_toast(toast)
        except FileNotFoundError:
            message = _(
                        "The file '$XDG_CONFIG_HOME/monitors.xml' is required to apply current"
                        " display settings but it does not exist.\n"
                        "\n"
                        "In order to create that file automatically,\n"
                        "\n"
                        "1. Go to 'Display' panel of System Settings.\n"
                        "2. Change some settings there.\n"
                        "3. Apply."
                       )

            dialog = Gtk.MessageDialog(
                             text = _('Monitor Settings Not Found'),
                            modal = True,
                          buttons = Gtk.ButtonsType.OK,
                     message_type = Gtk.MessageType.ERROR,
                    transient_for = self.window,
                   secondary_text = message,
             secondary_use_markup = True,
            )

            dialog.connect('response', lambda *args: dialog.close())
            dialog.present()
