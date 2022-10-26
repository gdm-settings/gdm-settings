#!/usr/bin/bash

# Dependencies
source "${ScriptDir}"/deps/Gtk.sh

echo 'Copying LibAdwaita'

# Files
copy /usr/lib/girepository-1.0/Adw-1.typelib
copy /usr/lib/libadwaita-1.so*
copy /usr/share/locale/*/LC_MESSAGES/libadwaita.mo
