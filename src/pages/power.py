import os
from gi.repository import Gtk
from ..info import data_dir
#from ..bind_utils import *
from .common import PageContent


class PowerPageContent (PageContent):
    __gtype_name__ = 'PowerPageContent'

    def __init__ (self, window, **kwargs):
        super().__init__(**kwargs)

        self.window = window

        self.builder = Gtk.Builder.new_from_file(os.path.join(data_dir, 'power-page.ui'))

        self.set_child(self.builder.get_object('content_box'))
