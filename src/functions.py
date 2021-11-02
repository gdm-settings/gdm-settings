#!/bin/python
'''Functions to be used by this project'''

import os, magic, re, shutil

from get_theme_list import ThemeList
import variables

def listdir_recursive(dir:str):
    files=[]
    for file in os.listdir(dir):
        if os.path.isdir(os.path.join(dir, file)):
            for subdir_file in listdir_recursive(os.path.join(dir, file)):
                files += [os.path.join(file, subdir_file)]
        else:
            files += [file]
    return files


def compile_theme(shellDir:str):
    # Copy gnome-shell dir of theme to temporary directory
    shutil.copytree(shellDir, variables.TempShellDir)
    # Inject custom-theme identity (doesn't work yet)
    CutomIdentity = open(os.path.join(variables.TempShellDir, variables.CustomThemeIdentity), 'w')
    CutomIdentity.write('yes')
    CutomIdentity.close()
    # Open /tmp/gdm-settings/gnome-shell/gnome-shell-theme.gresource.xml for writing
    GresourceXml = os.path.join(variables.TempShellDir, 'gnome-shell-theme.gresource.xml')
    GresourceXmlWrite = open(GresourceXml, 'w')

    # Fill gnome-shell-theme.gresource.xml
    GresourceXmlWrite.writelines(['<?xml version="1.0" encoding="UTF-8"?>',
                            '<gresources>',
                            ' <gresource prefix="/org/gnome/shell/theme">'])
    for file in listdir_recursive(shellDir):
        GresourceXmlWrite.write('  <file>' + file + '</file>')
    GresourceXmlWrite.writelines([' </gresource>',
                            '</gresources>'])
    GresourceXmlWrite.close()

    # Compile Theme
    os.system(f'glib-compile-resources --sourcedir={variables.TempShellDir} {variables.TempShellDir}/gnome-shell-theme.gresource.xml')
    shutil.move(os.path.join(variables.TempShellDir,'gnome-shell-theme.gresource'), variables.TempDir)
    shutil.rmtree(variables.TempShellDir)
    return  os.path.join(variables.TempDir,'gnome-shell-theme.gresource')

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
                print(f"'{background}' is not an image")
        else:
            print(f"file '{background}' does not exist")

def set_theme(args):
    if args.re_apply:
        print('re-apply')
    elif args.opt_background:
        set_background(args.opt_background)
    else:
        if not os.path.exists(variables.TempDir):
            os.mkdir(variables.TempDir)
        if args.background:
            set_background(args.background)
        print('theme: ' + args.theme)
        compiled_file = compile_theme(f'/usr/share/themes/{args.theme}/gnome-shell')
        os.system(f'{args.askpass} mv {compiled_file} {variables.GdmGresourceFile}')
        shutil.rmtree(variables.TempDir)
    
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
