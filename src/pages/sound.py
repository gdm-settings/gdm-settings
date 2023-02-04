import os
from gi.repository import Gtk
from ..utils import resource_path
from ..settings import sound_settings
from ..common_widgets import SwitchRow
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
        self.over_amplification_row = self.builder.get_object('over_amplification_row')
        self.event_sounds_row = self.builder.get_object('event_sounds_row')
        self.feedback_sounds_row = self.builder.get_object('feedback_sounds_row')

        self.theme_comborow.set_model(Gtk.StringList.new(sound_themes.names))
        self.bind_to_gsettings()

    def bind_to_gsettings (self):
        bind_comborow_by_list_alt(self.theme_comborow, sound_settings, 'theme', sound_themes.theme_ids)
        bind(sound_settings, 'event-sounds', self.event_sounds_row, 'enabled')
        bind(sound_settings, 'feedback-sounds', self.feedback_sounds_row, 'enabled')
        bind(sound_settings, 'over-amplification', self.over_amplification_row, 'enabled')
