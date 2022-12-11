import os
from gi.repository import Gtk
from ..utils import resource_path
from ..settings import font_settings
from ..bind_utils import *
from .common import PageContent


class FontsPageContent (PageContent):
    __gtype_name__ = 'FontsPageContent'

    def __init__ (self, window, **kwargs):
        super().__init__(**kwargs)

        self.window = window

        self.builder = Gtk.Builder.new_from_resource(resource_path('ui/fonts-page.ui'))

        self.set_child(self.builder.get_object('content_box'))

        self.font_button = self.builder.get_object('font_button')
        self.antialiasing_comborow = self.builder.get_object('antialiasing_comborow')
        self.hinting_comborow = self.builder.get_object('hinting_comborow')
        self.scaling_factor_spinbutton = self.builder.get_object('scaling_factor_spinbutton')

        # Following properties are ignored when set in .ui files.
        # So, they need to be changed here.
        self.scaling_factor_spinbutton.set_range(0.5, 3)
        self.scaling_factor_spinbutton.set_increments(0.1,0.5)

        self.bind_to_gsettings()

    def bind_to_gsettings (self):
        bind(font_settings, 'font', self.font_button, 'font')
        bind_comborow_by_list(self.antialiasing_comborow,
                font_settings, 'antialiasing', ['grayscale', 'rgba', 'none'])
        bind_comborow_by_list(self.hinting_comborow,
                font_settings, 'hinting', ['full', 'medium', 'slight', 'none'])
        bind(font_settings, 'scaling-factor', self.scaling_factor_spinbutton, 'value')
