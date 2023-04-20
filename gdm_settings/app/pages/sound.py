import os

from gi.repository import Gtk

from gdm_settings.lib import SwitchRow

from ..utils import resource_path
from ..settings import sound_settings
from ..theme_lists import sound_themes
from .common import PageContent


class SoundPageContent (PageContent):
    __gtype_name__ = 'SoundPageContent'

    def __init__ (self, window, **props):
        super().__init__(**props)

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
        sound_settings.bind_via_list('theme', self.theme_comborow, 'selected',
                                     sound_themes.theme_ids, strict=False)
        sound_settings.bind('event-sounds', self.event_sounds_row, 'enabled')
        sound_settings.bind('feedback-sounds', self.feedback_sounds_row, 'enabled')
        sound_settings.bind('over-amplification', self.over_amplification_row, 'enabled')
