#!/bin/python
'''Functions to be used by this project'''

import os, glob, magic, re, shutil
import variables


def get_theme_list():
    List=['default']
    for dir in sorted(glob.glob('/usr/share/themes/*'), key=str.casefold):
        if os.path.isfile(dir + "/gnome-shell/gnome-shell.css"):
            List.append(os.path.basename(dir))
    return List

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
    # Inject custom-theme identity
    open(os.path.join(variables.TempShellDir, variables.CustomThemeIdentity), 'w').close()

    # Open /tmp/gdm-settings/gnome-shell/gnome-shell-theme.gresource.xml for writing
    GresourceXml = os.path.join(variables.TempShellDir, 'gnome-shell-theme.gresource.xml')
    GresourceXmlWrite = open(GresourceXml, 'w')

    # Fill gnome-shell-theme.gresource.xml
    GresourceXmlWrite.writelines(['<?xml version="1.0" encoding="UTF-8"?>',
                            '<gresources>',
                            ' <gresource prefix="/org/gnome/shell/theme">'])
    for file in listdir_recursive(variables.TempShellDir):
        GresourceXmlWrite.write('  <file>' + file + '</file>')
    GresourceXmlWrite.writelines([' </gresource>',
                            '</gresources>'])
    GresourceXmlWrite.close()

    # Compile Theme
    os.system(f'glib-compile-resources --sourcedir={variables.TempShellDir} {variables.TempShellDir}/gnome-shell-theme.gresource.xml')
    shutil.move(os.path.join(variables.TempShellDir,'gnome-shell-theme.gresource'), variables.TempDir)
    shutil.rmtree(variables.TempShellDir)
    return  os.path.join(variables.TempDir,'gnome-shell-theme.gresource')

def set_background(background:str):
    if background == 'none':
        print('remove background')
    elif background in variables.AcceptableColors:
        print('background color name')
    elif re.fullmatch('^#(([0-9a-fA-F]){3}){1,2}$', background):
        print('background color code')
    else:
        if os.path.exists(background):
            if magic.detect_from_filename(background).mime_type.split('/')[0] == 'image':
                print('background image')
            else:
                print(f"'{background}' is not an image")
        else:
            print(f"file '{background}' does not exist")

def set_theme(theme:str, askpass:str="sudo"):
    if not os.path.exists(variables.TempDir):
        os.mkdir(variables.TempDir)
    print('theme: ' + theme)
    compiled_file = compile_theme(f'/usr/share/themes/{theme}/gnome-shell')
    os.system(f'{askpass} mv {compiled_file} {variables.GdmGresourceFile}')
    shutil.rmtree(variables.TempDir)
    
def print_theme_list():
    print(*get_theme_list(), sep='\n')
def print_color_list():
    print(*variables.AcceptableColors, sep='\n')
def backup_update():
    print('update backup')
def backup_restore():
    print('restore backup')
def extract_default_theme():
    print('extract default theme')
def show_manual(progName:str):
    os.system('man ' + progName)
def show_examples(progName:str):
    print('show examples')
