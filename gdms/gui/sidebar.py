from gi.repository import Adw
from gi.repository import Gtk
from gi.repository import GObject

from gdms.utils import GProperty


class SidebarItem(Adw.Bin):
    icon_name = GProperty(str)
    label = GProperty(str)
    clicked = GObject.Signal()

    def __init__(self, **props):
        super().__init__(**props)

        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 10)

        icon = Gtk.Image.new()
        self.bind_property("icon-name", icon, "icon-name")
        box.append(icon)

        label = Gtk.Label.new()
        self.bind_property("label", label, "label")
        box.append(label)

        click = Gtk.GestureClick.new()
        click.connect("released", self.on_click)

        self.props.child = box
        self.add_controller(click)

    def on_click(self, ctrl, n_press, x, y):
        self.emit("clicked")


class Sidebar(Adw.Bin):
    __gtype_name__ = 'GdmSettingsSidebar'

    stack = GProperty(Gtk.Stack)
    item_clicked = GObject.Signal()

    def __init__(self):
        super().__init__()

        selection = Gtk.SingleSelection()
        selection.connect("notify::selected", self.notify_selected_cb)

        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", self.setup_list_item)
        factory.connect("bind", self.bind_list_item)

        listview = Gtk.ListView.new(selection, factory)
        listview.add_css_class("navigation-sidebar")

        self.selection = selection
        self.props.child = listview
        self.connect("notify::stack", self.notify_stack_cb)

    @staticmethod
    def notify_stack_cb (this, prop):
        if this.stack:
            pages = this.stack.props.pages
            this.selection.props.model = pages
        else:
            this.selection.props.model = None

    def notify_selected_cb (self, selection, prop_name):
        self.stack.props.visible_child_name = selection.get_selected_item().get_name()

    def setup_list_item (self, factory, item: Gtk.ListItem):
        s_item = SidebarItem()
        s_item.connect("clicked", lambda x: self.emit("item-clicked"))
        item.props.child = s_item

    def bind_list_item (self, factory, item: Gtk.ListItem):
        page: Gtk.StackPage = item.props.item
        s_item: SidebarItem = item.props.child

        page.bind_property("icon-name", s_item, "icon-name", GObject.BindingFlags.SYNC_CREATE)
        page.bind_property("title", s_item, "label", GObject.BindingFlags.SYNC_CREATE)