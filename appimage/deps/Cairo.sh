#!/usr/bin/bash

echo 'Copying Cairo'

# Check Cairo version - directory only needed/exists for older versions
# The 1.18 threshold may be wrong, i.e., could be even earlier versions
CAIRO_VERSION=$(pkg-config --modversion cairo 2>/dev/null | cut -d. -f1,2)
if [ -n "$CAIRO_VERSION" ] && [ "$(echo "$CAIRO_VERSION < 1.18" | bc -l 2>/dev/null || echo 0)" -eq 1 ]; then
  # Older Cairo versions need the cairo directory
  try_copy \
    "${LIBDIR}/cairo" \
    "/usr/lib/cairo"
elif [ -d ${LIBDIR}/cairo ] || [ -d /usr/lib/cairo ]; then
  # If directory exists even on newer versions, copy it anyway
  try_copy \
    "${LIBDIR}/cairo" \
    "/usr/lib/cairo"
fi

copy ${LIBDIR}/libcairo*.so*
