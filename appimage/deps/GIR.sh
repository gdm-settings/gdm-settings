#!/usr/bin/bash

echo 'Copying GObject Introspection Runtime'

# AppRun Variables
echo 'export GI_TYPELIB_PATH="${AppDir}"/usr/lib/girepository-1.0' >> "${AppRun}"

# Files
copy ${LIBDIR}/girepository-1.0/DBus-1.0.typelib
copy ${LIBDIR}/girepository-1.0/DBusGLib-1.0.typelib
copy ${LIBDIR}/girepository-1.0/GIRepository-2.0.typelib
copy ${LIBDIR}/girepository-1.0/GL-1.0.typelib
copy ${LIBDIR}/girepository-1.0/GLib-2.0.typelib
copy ${LIBDIR}/girepository-1.0/GModule-2.0.typelib
copy ${LIBDIR}/girepository-1.0/GObject-2.0.typelib
copy ${LIBDIR}/girepository-1.0/Gio-2.0.typelib
copy ${LIBDIR}/girepository-1.0/Vulkan-1.0.typelib
copy ${LIBDIR}/girepository-1.0/cairo-1.0.typelib
copy ${LIBDIR}/girepository-1.0/fontconfig-2.0.typelib
copy ${LIBDIR}/girepository-1.0/freetype2-2.0.typelib
copy ${LIBDIR}/girepository-1.0/libxml2-2.0.typelib
copy ${LIBDIR}/girepository-1.0/xfixes-4.0.typelib
copy ${LIBDIR}/girepository-1.0/xft-2.0.typelib
copy ${LIBDIR}/girepository-1.0/xlib-2.0.typelib
copy ${LIBDIR}/girepository-1.0/xrandr-1.3.typelib
copy ${LIBDIR}/libgirepository-1.0.so*

# Only copy win32 typelib on Windows systems
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
  copy ${LIBDIR}/girepository-1.0/win32-1.0.typelib
fi
