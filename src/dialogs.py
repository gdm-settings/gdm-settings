from . import info
from gi.repository import Gtk

class AboutDialog (Gtk.AboutDialog):
    def __init__(self, win):
        Gtk.AboutDialog.__init__(self)
        self.props.transient_for  = win;
        self.props.modal          = True;
        self.props.license_type   = Gtk.License.AGPL_3_0;
        self.props.program_name   = info.application_name;
        self.props.logo_icon_name = info.application_id;
        self.props.version        =  f"{info.project_name} v{info.version}";
        self.props.comments       = _("A settings app for GNOME's Login Manager (GDM)");
        self.props.copyright      = _("Copyright © 2021 Mazhar Hussain");
        self.props.website_label  = _("Homepage");
        self.props.website        = "https://realmazharhussain.github.io/gdm-settings";

        self.props.authors     = [_("Mazhar Hussain") + " <mmazharhussainkgb1145@gmail.com>"]
        self.props.documenters = self.props.authors
        self.props.artists     = self.props.authors

        # Translators: Do not translate this string. Put your info here in the form
        # 'name <email>' including < and > but not qoutes.
        self.props.translator_credits = _("translator-credits")
