#!/usr/bin/bash

echo 'Copying Tracker'

# Files
copy ${LIBDIR}/girepository-1.0/Tracker-3.0.typelib
# Try both old (tracker) and new (tinysparql) library names
try_copy \
  "${LIBDIR}/libtracker-sparql-3.0.so*" \
  "${LIBDIR}/libtinysparql-3.0.so*"
copy ${LIBDIR}/tinysparql-3.0
try_copy_optional \
  "/usr/share/locale/*/LC_MESSAGES/tinysparql3.mo" \
  "/usr/share/locale-langpack/*/LC_MESSAGES/tinysparql3.mo"
