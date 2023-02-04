import os
from gi.repository import Gtk
from ..utils import resource_path
from ..settings import login_screen_settings
from ..common_widgets import ImageChooserButton, SwitchRow
from ..bind_utils import *
from .common import PageContent


class LoginScreenPageContent (PageContent):
    __gtype_name__ = 'LoginScreenPageContent'

    def __init__ (self, window, **kwargs):
        super().__init__(**kwargs)

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
        bind(login_screen_settings, 'disable-restart-buttons', self.disable_restart_buttons_row, 'enabled')
        bind(login_screen_settings, 'disable-user-list', self.disable_user_list_row, 'enabled')
        bind(login_screen_settings, 'enable-welcome-message', self.welcome_message_row, 'enabled')
        bind(login_screen_settings, 'enlarge-welcome-message', self.enlarge_welcome_message_row, 'enabled')
        bind(login_screen_settings, 'welcome-message', self.welcome_message_entryrow, 'text')
        bind(login_screen_settings, 'enable-logo', self.logo_switch, 'active')
        bind(login_screen_settings, 'logo', self.logo_button, 'filename')
