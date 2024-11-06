#!/usr/bin/bash

echo 'Copying Python'

# Dependencies
copy /usr/lib/libffi.so*

# Files
copy /usr/bin/python3*
copy /usr/lib/libpython3*.so*

for file in /usr/lib/python3.*/*; do
  if test "$(basename "${file}")" != site-packages; then
    copy "${file}"
  fi
done


echo 'Copying PyGObject'
copy /usr/lib/python3.*/site-packages/gi
copy /usr/lib/python3.*/site-packages/pygtkcompat
