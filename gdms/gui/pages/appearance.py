from gettext import gettext as _

from gi.repository import Gtk
from gi.repository import GObject

from gdms.enums import BackgroundType
from gdms.utils import GProperty
from gdms.themes import shell_themes, icon_themes, cursor_themes
from gdms.settings import appearance_settings
from gdms.gui.widgets import ImageChooserButton

from .common import PageContent


class AppearancePageContent (PageContent):
    __gtype_name__ = 'AppearancePageContent'

    def __init__ (self, window, **props):
        super().__init__(**props)

        self.window = window

        self.builder = Gtk.Builder.new_from_resource('/app/ui/appearance-page.ui')

        self.set_child(self.builder.get_object('content_box'))

        self.accent_selector = self.builder.get_object('accent_selector')

        self.shell_theme_comborow = self.builder.get_object('shell_theme_comborow')
        self.icon_theme_comborow = self.builder.get_object('icon_theme_comborow')
        self.cursor_theme_comborow = self.builder.get_object('cursor_theme_comborow')

        self.background_type_comborow = self.builder.get_object('background_type_comborow')
        self.bg_img_adj_comborow = self.builder.get_object('bg_img_adj_comborow')
        self.background_image_actionrow = self.builder.get_object('background_image_actionrow')
        self.background_color_actionrow = self.builder.get_object('background_color_actionrow')
        self.background_color_button = self.builder.get_object('background_color_button')

        # Add background image button
        self.background_image_button = ImageChooserButton(valign='center')
        self.background_image_actionrow.add_suffix(self.background_image_button)
        self.background_image_actionrow.set_activatable_widget(self.background_image_button)

        self.background_type_comborow.connect('notify::selected', self.on_background_type_changed)

        self.load_theme_lists()
        self.bind_to_gsettings()


    def on_background_type_changed (self, comborow, prop):
        background_type = BackgroundType(comborow.get_selected())
        if background_type is BackgroundType.image:
            self.background_image_actionrow.set_visible(True)
            self.background_color_actionrow.set_visible(False)
        elif background_type is BackgroundType.color:
            self.background_image_actionrow.set_visible(False)
            self.background_color_actionrow.set_visible(True)
        else:
            self.background_image_actionrow.set_visible(False)
            self.background_color_actionrow.set_visible(False)


    def load_theme_lists(self):
        def load_list(comborow, lyst):
            comborow.set_model(Gtk.StringList.new(lyst.names))

        load_list(self.shell_theme_comborow, shell_themes)
        load_list(self.icon_theme_comborow, icon_themes)
        load_list(self.cursor_theme_comborow, cursor_themes)


    def bind_to_gsettings (self):
        appearance_settings.bind('accent-color', self.accent_selector, 'selected')
        appearance_settings.bind_via_list('shell-theme', self.shell_theme_comborow, 'selected',
                                          shell_themes.theme_ids, strict=False)
        appearance_settings.bind_via_list('icon-theme', self.icon_theme_comborow, 'selected',
                                          icon_themes.theme_ids, strict=False)
        appearance_settings.bind_via_list('cursor-theme', self.cursor_theme_comborow, 'selected',
                                          cursor_themes.theme_ids, strict=False)
        appearance_settings.bind_via_enum('background-type', self.background_type_comborow,
                                          'selected', BackgroundType)
        appearance_settings.bind_via_list('bg-adjustment', self.bg_img_adj_comborow, 'selected',
                                          ['zoom', 'repeat'])
        appearance_settings.bind('background-image', self.background_image_button, 'filename')
        appearance_settings.bind_to_colorbutton('background-color', self.background_color_button)


class AccentButton (Gtk.ToggleButton):
    __gtype_name__ = 'AccentButton'
    accent: str = GProperty(str, construct_only=True)

    def __init__(self, accent: str, **props):
        super().__init__(accent = accent, **props)
        self.add_css_class('accent')
        self.add_css_class(accent)


class AccentSelector (Gtk.Box):
    __gtype_name__ = 'AccentSelector'

    accents = {
        'blue' : _('Blue'),
        'teal' : _('Teal'),
        'green' : _('Green'),
        'yellow' : _('Yellow'),
        'orange' : _('Orange'),
        'red' : _('Red'),
        'pink' : _('Pink'),
        'purple' : _('Purple'),
        'slate' : _('Slate'),
    }

    selected: str = GProperty(str, default="blue")
    compact: str = GProperty(bool, default=False)

    def __init__(self, **props):
        super().__init__(**props)
        self.props.halign = Gtk.Align.CENTER
        self.props.valign = Gtk.Align.CENTER

        self.connect("notify::compact", self.on_notify_compact)

        # Add children
        for accent, tooltip in self.accents.items():
            self.append(AccentButton(accent, tooltip_text = tooltip))

        # Set up toggle group
        group = self.get_first_child()
        child = group.get_next_sibling()
        while isinstance(child, AccentButton):
            child.props.group = group
            child = child.get_next_sibling()

        # Connect signals
        child = self.get_first_child()
        while isinstance(child, AccentButton):
            child.connect("toggled", lambda x: x.props.active and self.on_accent_selected(x))
            child = child.get_next_sibling()

        # Update UI when 'selected' property is changed programatically
        self.connect("notify::selected", self.on_notify_selected)
        self.on_notify_selected()

    def on_accent_selected(self, btn: AccentButton):
        self.selected = btn.accent

    def on_notify_compact(self, x=None, y=None):
        if self.compact:
            self.add_css_class("compact")
        else:
            self.remove_css_class("compact")

    def on_notify_selected(self, x=None, y=None):
        child = self.get_first_child()
        while isinstance(child, AccentButton):
            child.props.active = child.accent == self.selected
            child = child.get_next_sibling()
