import os

from gi.repository import Gtk

from gdm_settings.widgets import ImageChooserButton, SwitchRow

from ..utils import resource_path
from ..settings import login_screen_settings
from .common import PageContent


class LoginScreenPageContent (PageContent):
    __gtype_name__ = 'LoginScreenPageContent'

    def __init__ (self, window, **props):
        super().__init__(**props)

        self.window = window

        self.builder = Gtk.Builder.new_from_resource(resource_path('ui/login-screen-page.ui'))

        self.set_child(self.builder.get_object('content_box'))

        self.disable_restart_buttons_row = self.builder.get_object('disable_restart_buttons_row')
        self.disable_user_list_row = self.builder.get_object('disable_user_list_row')
        self.welcome_message_row = self.builder.get_object('welcome_message_row')
        self.welcome_message_entryrow = self.builder.get_object('welcome_message_entryrow')
        self.enlarge_welcome_message_row = self.builder.get_object('enlarge_welcome_message_row')
        self.logo_actionrow = self.builder.get_object('logo_actionrow')
        self.logo_switch = self.builder.get_object('logo_switch')

        # Add logo button
        self.logo_button = ImageChooserButton(valign='center')
        self.logo_actionrow.add_suffix(self.logo_button)
        self.logo_actionrow.set_activatable_widget(self.logo_button)

        self.bind_to_gsettings()

    def bind_to_gsettings (self):
        login_screen_settings.bind('disable-restart-buttons', self.disable_restart_buttons_row, 'enabled')
        login_screen_settings.bind('disable-user-list', self.disable_user_list_row, 'enabled')
        login_screen_settings.bind('enable-welcome-message', self.welcome_message_row, 'enabled')
        login_screen_settings.bind('enlarge-welcome-message', self.enlarge_welcome_message_row, 'enabled')
        login_screen_settings.bind('welcome-message', self.welcome_message_entryrow, 'text')
        login_screen_settings.bind('enable-logo', self.logo_switch, 'active')
        login_screen_settings.bind('logo', self.logo_button, 'filename')
