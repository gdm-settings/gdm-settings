#!/bin/python
'''Get list of installed GDM themes'''

import os, glob

def get_theme_list():
    List=['default']
    for dir in sorted(glob.glob('/usr/share/themes/*'), key=str.casefold):
        if os.path.isfile(dir + "/gnome-shell/gnome-shell.css"):
            List.append(os.path.basename(dir))
    return List

ThemeList=get_theme_list()