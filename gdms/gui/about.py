from gettext import gettext as _, pgettext as C_

from gi.repository import Adw

from gdms import VERSION, temp_log_io


mazhar_hussain = C_("Name of Developer", "Mazhar Hussain") + " <realmazharhussain@gmail.com>"
thales_binda   = C_("Name of Artist",    "Thales Bindá") +   " <thales.i.o.b@gmail.com>"


def about_window(win):
    temp_log_io.seek(0)

    abt = Adw.AboutWindow.new_from_appdata("/app/info.xml")
    abt.set_properties(
        artists = [thales_binda],
        copyright = _("Copyright 2021-2023 Mazhar Hussain"),
        debug_info = temp_log_io.read(),
        debug_info_filename = 'gdm-settings.log',
        developers = [mazhar_hussain],
        documenters = [mazhar_hussain],
        transient_for = win,
        version = VERSION,

        # Translators: Do not translate this string. Put your info here in the form
        # 'name <email>' including < and > but not quotes.
        translator_credits = _("translator-credits"),
    )

    return abt
