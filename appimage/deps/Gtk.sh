#!/bin/bash

# Dependencies
source "${ScriptDir}"/deps/GLib.sh
source "${ScriptDir}"/deps/LibRsvg.sh
source "${ScriptDir}"/deps/Pango.sh
source "${ScriptDir}"/deps/Cairo.sh
source "${ScriptDir}"/deps/Tracker.sh
source "${ScriptDir}"/deps/Graphene.sh
source "${ScriptDir}"/deps/HarfBuzz.sh
source "${ScriptDir}"/deps/Gdk-Pixbuf.sh
source "${ScriptDir}"/deps/CloudProviders.sh

echo 'Installing GTK'

# Dependencies
copy /usr/lib/libfreetype.so*
copy /usr/lib/libfribidi.so*
copy /usr/lib/libstemmer.so*
copy /usr/lib/libicu*.so*
copy /usr/lib/libfontconfig.so*
copy /usr/lib/libwayland-*.so*

# Files
copy /usr/lib/gtk-4.0
copy /usr/lib/libgtk-4.so*
copy /usr/lib/girepository-1.0/Gdk-4.0.typelib
copy /usr/lib/girepository-1.0/GdkWayland-4.0.typelib
copy /usr/lib/girepository-1.0/GdkX11-4.0.typelib
copy /usr/lib/girepository-1.0/Gsk-4.0.typelib
copy /usr/lib/girepository-1.0/Gtk-4.0.typelib
copy /usr/share/gtk-4.0
copy /usr/share/glib-2.0/schemas/org.gtk.gtk4.Settings.*.gschema.xml
copy /usr/share/locale/*/LC_MESSAGES/gtk40.mo
