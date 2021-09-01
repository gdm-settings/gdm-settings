#!/bin/python
'''Get list of installed GDM themes'''

import os, glob

ThemeList=['default']
for dir in sorted(glob.glob('/usr/share/themes/*'), key=str.casefold):
    if os.path.isfile(dir + "/gnome-shell/gnome-shell.css"):
        ThemeList.append(os.path.basename(dir))
