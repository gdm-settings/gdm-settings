from gi.repository import Adw, Gtk


class PageContent (Gtk.ScrolledWindow):
    '''Base class for content of a page from Gtk.Stack'''
    def __init__ (self, **kwargs):
        super().__init__(**kwargs)

        self.set_propagate_natural_height(True)

        margin=20
        self.clamp = Adw.Clamp(maximum_size=2000, tightening_threshold=300)
        self.clamp.set_margin_top(margin)
        self.clamp.set_margin_bottom(margin)
        self.clamp.set_margin_start(margin)
        self.clamp.set_margin_end(margin)
        super().set_child(self.clamp)

    def set_child (self, child):
        self.clamp.set_child(child)
