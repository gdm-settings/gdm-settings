import os
from gi.repository import Gtk
from ..utils import resource_path
from ..settings import sound_settings
from ..theme_lists import sound_themes
from ..bind_utils import *
from .common import PageContent


class SoundPageContent (PageContent):
    __gtype_name__ = 'SoundPageContent'

    def __init__ (self, window, **kwargs):
        super().__init__(**kwargs)

        self.window = window

        self.builder = Gtk.Builder.new_from_resource(resource_path('ui/sound-page.ui'))

        self.set_child(self.builder.get_object('content_box'))

        self.theme_comborow = self.builder.get_object('theme_comborow')
        self.over_amplification_switch = self.builder.get_object('over_amplification_switch')
        self.event_sounds_switch = self.builder.get_object('event_sounds_switch')
        self.feedback_sounds_switch = self.builder.get_object('feedback_sounds_switch')

        self.load_theme_list()
        self.bind_to_gsettings()

    def load_theme_list (self):
        sound_theme_list = Gtk.StringList()
        for theme_name in sound_themes.names:
            sound_theme_list.append(theme_name)
        self.theme_comborow.set_model(sound_theme_list)

    def bind_to_gsettings (self):
        bind_comborow(self.theme_comborow, sound_settings, 'theme')
        bind(sound_settings, 'event-sounds', self.event_sounds_switch, 'active')
        bind(sound_settings, 'feedback-sounds', self.feedback_sounds_switch, 'active')
        bind(sound_settings, 'over-amplification', self.over_amplification_switch, 'active')
