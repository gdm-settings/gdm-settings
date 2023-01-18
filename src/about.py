from gettext import gettext as _, pgettext as C_
from gi.repository import Adw, Gtk
from . import info

mazhar_hussain = C_("Name of Developer", "Mazhar Hussain") + " <realmazharhussain@gmail.com>"
thales_binda   = C_("Name of Artist",    "Thales Bindá") +   " <thales.i.o.b@gmail.com>"

release_notes=_('''
<p><em>New Options</em></p>
<ul>
  <li>Option to change cursor size</li>
  <li>Donate option in hamburger menu</li>
</ul>
<p><em>Behavior Changes</em></p>
<ul>
  <li>Proper names are shown for themes instead of name of their directory</li>
  <li>Cursor themes are not presented when choosing icon theme</li>
</ul>
''')

def about_window(win):
    return Adw.AboutWindow(
        transient_for = win,
        modal         = True,
        application_name = info.application_name,
        application_icon = info.application_id,
        license_type     = Gtk.License.AGPL_3_0,
        version          = info.version,
        developer_name   = C_("Name of Developer", "Mazhar Hussain"),
        copyright = _("Copyright 2021-2022 Mazhar Hussain"),
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
