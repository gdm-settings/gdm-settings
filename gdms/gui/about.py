from gettext import gettext as _, pgettext as C_

from gi.repository import Adw
from gi.repository import Gtk

from gdms import APP_ID, APP_NAME, VERSION, temp_log_io


mazhar_hussain = C_("Name of Developer", "Mazhar Hussain") + " <realmazharhussain@gmail.com>"
thales_binda   = C_("Name of Artist",    "Thales Bindá") +   " <thales.i.o.b@gmail.com>"


def about_window(win):
    temp_log_io.seek(0)

    abt = Adw.AboutWindow(
        transient_for = win,
        modal         = True,
        application_name = APP_NAME,
        application_icon = APP_ID,
        license_type     = Gtk.License.AGPL_3_0,
        version          = VERSION,
        developer_name   = C_("Name of Developer", "Mazhar Hussain"),
        copyright = _("Copyright 2021-2023 Mazhar Hussain"),
        website   = "https://gdm-settings.github.io",
        debug_info = temp_log_io.read(),
        developers  = [mazhar_hussain],
        documenters = [mazhar_hussain],
        artists     = [thales_binda],
        debug_info_filename = 'gdm-settings.log',

        support_url = "https://github.com/gdm-settings/gdm-settings/discussions/categories/q-a",
        issue_url   = "https://github.com/gdm-settings/gdm-settings/issues/new/choose",

        # Translators: Do not translate this string. Put your info here in the form
        # 'name <email>' including < and > but not quotes.
        translator_credits = _("translator-credits"),
        )

    return abt
