#!/usr/bin/bash

echo 'Copying Python'

# Detect Python packages directory (dist-packages on Debian/Ubuntu, site-packages elsewhere)
if [ -d /usr/lib/python3*/dist-packages ]; then
  PYTHON_PKGDIR=/usr/lib/python3*/dist-packages
else
  PYTHON_PKGDIR=/usr/lib/python3.*/site-packages
fi

# Dependencies
copy ${LIBDIR}/libffi.so*

# Files
copy /usr/bin/python3*
copy ${LIBDIR}/libpython3*.so*

for file in /usr/lib/python3.*/*; do
  if test "$(basename "${file}")" != site-packages; then
    copy "${file}"
  fi
done


echo 'Copying PyGObject'
copy ${PYTHON_PKGDIR}/gi
copy ${PYTHON_PKGDIR}/pygtkcompat
