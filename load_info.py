#!/usr/bin/env python3
import gettext
gettext.install('gdm-settings')

from build.src.info import *
print(f"project_name='{project_name}'")
print(f"application_name='{application_name}'")
print(f"version='{version}'")
print(f"application_id='{application_id}'")

print(f"py_modules_dir='{py_modules_dir}'")
