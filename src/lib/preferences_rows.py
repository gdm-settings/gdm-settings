from gi.repository import Adw
from gi.repository import Gtk
from gi.repository import GObject


__all__ = ['SwitchRow']


class SwitchRow (Adw.ActionRow):
    __gtype_name__ = 'SwitchRow'

    enabled = GObject.Property(type=bool, default=False)

    def __init__ (self, **props):
        super().__init__(**props)

        switch = Gtk.Switch(valign=Gtk.Align.CENTER)
        switch.bind_property('active', self, 'enabled',
                             GObject.BindingFlags.SYNC_CREATE|GObject.BindingFlags.BIDIRECTIONAL)
        self.add_suffix(switch)
        self.set_activatable_widget(switch)
