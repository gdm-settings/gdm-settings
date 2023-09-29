from gi.repository import Gtk

from gdms.settings import font_settings
from .common import PageContent


class FontsPageContent (PageContent):
    __gtype_name__ = 'FontsPageContent'

    def __init__ (self, window, **props):
        super().__init__(**props)

        self.window = window

        self.builder = Gtk.Builder.new_from_resource('/app/ui/fonts-page.ui')

        self.set_child(self.builder.get_object('content_box'))

        self.font_button = self.builder.get_object('font_button')
        self.antialiasing_comborow = self.builder.get_object('antialiasing_comborow')
        self.hinting_comborow = self.builder.get_object('hinting_comborow')
        self.scaling_factor_spinrow = self.builder.get_object('scaling_factor_spinrow')

        self.bind_to_gsettings()

    def bind_to_gsettings (self):
        font_settings.bind('font', self.font_button, 'font')
        font_settings.bind_via_list('antialiasing', self.antialiasing_comborow, 'selected',
                                    ['grayscale', 'rgba', 'none'])
        font_settings.bind_via_list('hinting', self.hinting_comborow, 'selected',
                                    ['full', 'medium', 'slight', 'none'])
        font_settings.bind('scaling-factor', self.scaling_factor_spinrow, 'value')
