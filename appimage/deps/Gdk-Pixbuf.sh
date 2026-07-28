#!/usr/bin/bash

echo 'Copying Gdk Pixbuf'

# Dependencies
copy ${LIBDIR}/libjpeg.so*
copy ${LIBDIR}/libturbojpeg.so*

# Files
copy ${LIBDIR}/girepository-1.0/GdkPix*-2.0.typelib
copy ${LIBDIR}/libgdk_pixbuf-2.0.so*
try_copy_optional \
  "/usr/share/locale/*/LC_MESSAGES/gdk-pixbuf.mo" \
  "/usr/share/locale-langpack/*/LC_MESSAGES/gdk-pixbuf.mo"


echo 'Copying Gdk Pixbuf Loaders'

moduledir=$(pkgconf --variable gdk_pixbuf_moduledir gdk-pixbuf-2.0)
cache_file=$(pkgconf --variable gdk_pixbuf_cache_file gdk-pixbuf-2.0)

# Files
copy "${moduledir}"

# Try both /usr/bin and multiarch locations for gdk-pixbuf-query-loaders
if command -v gdk-pixbuf-query-loaders >/dev/null 2>&1; then
  gdk-pixbuf-query-loaders | sed "s|${moduledir}/||g" > "${AppDir}/${cache_file}"
elif [ -x ${LIBDIR}/gdk-pixbuf-2.0/gdk-pixbuf-query-loaders ]; then
  ${LIBDIR}/gdk-pixbuf-2.0/gdk-pixbuf-query-loaders | sed "s|${moduledir}/||g" > "${AppDir}/${cache_file}"
else
  echo "Error: gdk-pixbuf-query-loaders not found"
  exit 1
fi
