from gettext import gettext as _, pgettext as C_

from gi.repository import Adw, Gtk

from . import info

mazhar_hussain = C_("Name of Developer", "Mazhar Hussain") + " <realmazharhussain@gmail.com>"
thales_binda   = C_("Name of Artist",    "Thales Bindá") +   " <thales.i.o.b@gmail.com>"

# FIXME: xgettext extracts each list item or paragraph from the release description in the
# metainfo file separately. So, if we don't want to be translating the same content twice,
# we need to separate translatable parts.
release_notes=(
    '<p>' + _('<em>New Options</em>') + '</p>\n'
    '<ul>\n'
    '  <li>' + _('Option to change cursor size') + '</li>\n'
    '  <li>' + _('Donate option in hamburger menu') + '</li>\n'
    '</ul>\n'
    '<p>' + _('<em>Behavior Changes</em>') + '</p>\n'
    '<ul>\n'
    '  <li>' + _('Proper names are shown for themes instead of name of their directory') + '</li>\n'
    '  <li>' + _('Cursor themes are not presented when choosing icon theme') + '</li>\n'
    '</ul>'
)

def about_window(win):
    return Adw.AboutWindow(
        transient_for = win,
        modal         = True,
        application_name = info.application_name,
        application_icon = info.application_id,
        license_type     = Gtk.License.AGPL_3_0,
        version          = info.version,
        developer_name   = C_("Name of Developer", "Mazhar Hussain"),
        copyright = _("Copyright 2021-2023 Mazhar Hussain"),
        website   = "https://realmazharhussain.github.io/gdm-settings",
        developers  = [mazhar_hussain],
        designers   = [mazhar_hussain],
        documenters = [mazhar_hussain],
        artists     = [thales_binda],

        support_url = "https://github.com/realmazharhussain/gdm-settings/discussions/categories/q-a",
        issue_url   = "https://github.com/realmazharhussain/gdm-settings/issues/new/choose",

        release_notes    = release_notes,
        release_notes_version = info.version,

        # Translators: Do not translate this string. Put your info here in the form
        # 'name <email>' including < and > but not quotes.
        translator_credits = _("translator-credits"),
        )
