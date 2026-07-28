#!/usr/bin/bash

echo 'Copying GLib'

# Dependencies
copy ${LIBDIR}/libpcre*.so*

# Files
copy /usr/bin/glib-compile-resources
copy ${LIBDIR}/libgio-2.0.so*
copy ${LIBDIR}/libglib-2.0.so*
copy ${LIBDIR}/libgmodule-2.0.so*
copy ${LIBDIR}/libgobject-2.0.so*
copy ${LIBDIR}/libgthread-2.0.so*
try_copy_optional \
  "/usr/share/locale/*/LC_MESSAGES/glib20.mo" \
  "/usr/share/locale-langpack/*/LC_MESSAGES/glib20.mo"
