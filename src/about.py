from gettext import gettext as _, pgettext as C_
from gi.repository import Adw, Gtk
from . import info

mazhar_hussain = C_("Name of Developer", "Mazhar Hussain") + " <realmazharhussain@gmail.com>"
thales_binda   = C_("Name of Artist",    "Thales Bindá") +   " <thales.i.o.b@gmail.com>"

def about_window(win):
    return Adw.AboutWindow(
        transient_for = win,
        modal         = True,
        application_name = info.application_name,
        application_icon = info.application_id,
        license_type     = Gtk.License.AGPL_3_0,
        version          = info.version,
        developer_name   = "Mazhar Hussain",
        copyright = _("Copyright © 2021 Mazhar Hussain"),
        website   = "https://realmazharhussain.github.io/gdm-settings",
        developers  = [mazhar_hussain],
        designers   = [mazhar_hussain],
        documenters = [mazhar_hussain],
        artists     = [thales_binda],

        support_url = "https://github.com/realmazharhussain/gdm-settings/discussions/categories/q-a",
        issue_url   = "https://github.com/realmazharhussain/gdm-settings/issues/new/choose",

        # Translators: Do not translate this string. Put your info here in the form
        # 'name <email>' including < and > but not qoutes.
        translator_credits = _("translator-credits"),
        )
