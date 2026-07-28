#!/usr/bin/bash

echo 'Copying Pango'

# Dependencies
copy ${LIBDIR}/libbz2.so*

# Files
copy ${LIBDIR}/girepository-1.0/Pango*-1.0.typelib
copy ${LIBDIR}/libpango*-1.0.so*
