#!/usr/bin/bash

echo 'Copying GLib'

# Dependencies
copy /usr/lib/libpcre.so*

# Files
copy_bin glib-compile-resources
copy /usr/lib/libgio-2.0.so*
copy /usr/lib/libglib-2.0.so*
copy /usr/lib/libgmodule-2.0.so*
copy /usr/lib/libgobject-2.0.so*
copy /usr/lib/libgthread-2.0.so*
copy /usr/share/locale/*/LC_MESSAGES/glib20.mo
