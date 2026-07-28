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

echo 'Copying GTK'

# Dependencies
copy ${LIBDIR}/libfreetype.so*
copy ${LIBDIR}/libfribidi.so*
copy ${LIBDIR}/libstemmer.so*
copy ${LIBDIR}/libicu*.so*
copy ${LIBDIR}/libfontconfig.so*
copy ${LIBDIR}/libwayland-*.so*

# Files
copy ${LIBDIR}/gtk-4.0
copy ${LIBDIR}/libgtk-4.so*
copy ${LIBDIR}/girepository-1.0/Gdk-4.0.typelib
copy ${LIBDIR}/girepository-1.0/GdkWayland-4.0.typelib
copy ${LIBDIR}/girepository-1.0/GdkX11-4.0.typelib
copy ${LIBDIR}/girepository-1.0/Gsk-4.0.typelib
copy ${LIBDIR}/girepository-1.0/Gtk-4.0.typelib
copy /usr/share/gtk-4.0
copy /usr/share/glib-2.0/schemas/org.gtk.gtk4.Settings.*.gschema.xml
try_copy_optional \
  "/usr/share/locale/*/LC_MESSAGES/gtk40.mo" \
  "/usr/share/locale-langpack/*/LC_MESSAGES/gtk40.mo"
