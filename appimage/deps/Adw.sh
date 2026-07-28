#!/usr/bin/bash

# Dependencies
source "${ScriptDir}"/deps/Gtk.sh

echo 'Copying LibAdwaita'

# Files
copy ${LIBDIR}/girepository-1.0/Adw-1.typelib
copy ${LIBDIR}/libadwaita-1.so*
try_copy_optional \
  "/usr/share/locale/*/LC_MESSAGES/libadwaita.mo" \
  "/usr/share/locale-langpack/*/LC_MESSAGES/libadwaita.mo"
