#!/bin/python
'''Functions to be used by this project'''

import os, magic, re

from get_theme_list import ThemeList
import variables

def set_background(background):
    if background == 'none':
        print('remove background')
    elif background in variables.AcceptableColors:
        print('background color name')
    elif re.fullmatch('^#(([0-9a-fA-F]){3}){1,2}$', background):
        print('background color code')
    else:
        if os.path.exists(background):
            if 'image' == magic.detect_from_filename(background).mime_type.split('/')[0]:
                print('background image')
            else:
                print("'"+background+"'", 'is not an image')
        else:
            print('file', "'"+background+"'", 'does not exist')

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