#!/bin/python

import os

from get_theme_list import ThemeList
import variables

def set_background(background):
    print('background: ' + background)
def set_theme(args):
    if args.re_apply:
        print('re-apply')
    elif args.opt_background:
        set_background(args.opt_background)
    else:
        if args.background:
            set_background(args.background)
        print('theme: ' + args.theme)
    
def list_themes(args):
    print(*ThemeList, sep='\n')
def list_colors(args):
    print(*variables.AcceptableColors, sep='\n')
def backup_update(args):
    print('update backup')
def backup_restore(args):
    print('restore backup')
def extract_default_theme(args):
    print('extract default theme')
def show_manual(args):
    os.system('man ' + args.prog)
def show_examples(args):
    print('show examples')