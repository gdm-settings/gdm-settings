#!/usr/bin/env python3
import gettext
gettext.install('gdm-settings')

from sys import argv

info = ""
with open (argv[1]) as info_file:
    info = info_file.read()
exec(info)

print(f"project_name='{project_name}'")
print(f"application_name='{application_name}'")
print(f"version='{version}'")
print(f"application_id='{application_id}'")

print(f"py_modules_dir='{py_modules_dir}'")
