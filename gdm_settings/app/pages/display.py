import logging
from gettext import gettext as _, pgettext as C_

from gi.repository import Adw
from gi.repository import Gtk

from gdm_settings.utils import BackgroundTask
from gdm_settings.widgets import SwitchRow
from gdm_settings.settings import night_light_settings as nl_settings
from gdm_settings import settings

from .common import PageContent

logger = logging.getLogger(__name__)


class DisplayPageContent (PageContent):
    __gtype_name__ = 'DisplayPageContent'

    def __init__ (self, window, **props):
        super().__init__(**props)

        self.window = window

        self.builder = Gtk.Builder.new_from_resource('/app/ui/display-page.ui')

        self.set_child(self.builder.get_object('content_box'))

        self.apply_display_settings_button = self.builder.get_object('apply_display_settings_button')
        self.apply_display_settings_button.connect('clicked', self.on_apply_display_settings)

        self.nl_enable_row = self.builder.get_object('nl_enable_row')
        self.nl_schedule_comborow = self.builder.get_object('nl_schedule_comborow')
        self.nl_start_box = self.builder.get_object('nl_start_box')
        self.nl_start_hour_spinbutton = self.builder.get_object('nl_start_hour_spinbutton')
        self.nl_start_minute_spinbutton = self.builder.get_object('nl_start_minute_spinbutton')
        self.nl_end_box = self.builder.get_object('nl_end_box')
        self.nl_end_hour_spinbutton = self.builder.get_object('nl_end_hour_spinbutton')
        self.nl_end_minute_spinbutton = self.builder.get_object('nl_end_minute_spinbutton')
        self.nl_temperature_scale = self.builder.get_object('nl_temperature_scale')

        self.apply_display_settings_task = BackgroundTask(settings.apply_user_display_settings,
                                                          self.on_apply_display_settings_finish)

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
        nl_settings.bind('enabled', self.nl_enable_row, 'enabled')
        nl_settings.bind_via_list('schedule-automatic', self.nl_schedule_comborow, 'selected',
                                  [True, False])
        nl_settings.bind('start-hour', self.nl_start_hour_spinbutton, 'value')
        nl_settings.bind('start-minute', self.nl_start_minute_spinbutton, 'value')
        nl_settings.bind('end-hour', self.nl_end_hour_spinbutton, 'value')
        nl_settings.bind('end-minute', self.nl_end_minute_spinbutton, 'value')
        nl_settings.bind('temperature', self.nl_temperature_scale.props.adjustment, 'value')

    def on_apply_display_settings (self, button):
        self.window.task_counter.inc()
        self.apply_display_settings_task.start()

    def on_apply_display_settings_finish(self):
        self.window.task_counter.dec()
        try:
            status = self.apply_display_settings_task.finish()
            if status.success:
                message = _("Applied current display settings")
            else:
                message = _("Failed to apply current display settings")
            toast = Adw.Toast(timeout=2, priority="high", title=message)
            self.window.toast_overlay.add_toast(toast)
        except FileNotFoundError as err:
            logger.debug(f"{err.strerror}: '{err.filename}'")

            message = _("'$XDG_CONFIG_HOME/monitors.xml' file is required to apply current"
                        " display settings but it does not exist.\n"
                        "\n"
                        "In order to create that file automatically, open system 'Settings'"
                        " and change some display options there.")

            dialog = Adw.MessageDialog(
                        body = message,
                       modal = True,
                     heading = _('Monitor Settings Not Found'),
               transient_for = self.window,
             body_use_markup = True,
            )

            dialog.add_response('ok', _('OK'))
            dialog.present()
