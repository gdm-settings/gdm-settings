'''Miscellaneos Functions to be used by this project'''

import os
import glob
import shutil
import subprocess

from info import *
from command_elevation import *
elevated_commands_list = ElevatedCommandsList()

def listdir_recursive(dir:str):
    """list files (only) inside a directory recursively"""

    files=[]
    for file in os.listdir(dir):
        if os.path.isdir(os.path.join(dir, file)):
            for subdir_file in listdir_recursive(os.path.join(dir, file)):
                files += [os.path.join(file, subdir_file)]
        else:
            files += [file]
    return files

def get_theme_list():
    """get a list of installed gnome-shell/GDM themes"""

    List=['default']
    for dir in sorted(glob.glob('/usr/share/themes/*'), key=str.casefold):
        if os.path.isfile(dir + "/gnome-shell/gnome-shell.css"):
            List.append(os.path.basename(dir))
    return List

def is_default_gresource_file(gresourceFile:str):
    """checks if the provided file is a GResource file of the default theme"""

    if os.path.exists(gresourceFile):
        if subprocess.getoutput(f"gresource list {gresourceFile} /org/gnome/shell/theme/gnome-shell.css"):
            if not subprocess.getoutput(f"gresource list {gresourceFile} /org/gnome/shell/theme/{CustomThemeIdentity}"):
                return True
    return False

def get_default_gresource_file() -> str:
    """get full path to the GResource file of the default theme (if the file exists)"""

    for file in GdmGresourceFile, GdmGresourceAutoBackup, GdmGresourceManualBackup:
       if is_default_gresource_file(file):
           return file

def extract_theme_from_gresource_file(gresource_file:str):
    """extracts theme resources from provided GResource file of the theme
    
    Returns: path to a directory inside which resources of the theme were extracted"""

    TempExtractedDir = f"{TempDir}/extracted"
    resource_list = subprocess.getoutput(f"gresource list {gresource_file}").splitlines()
    for resource in resource_list:
        filename = resource.removeprefix("/org/gnome/shell/theme/")
        filepath = os.path.join(TempExtractedDir, filename)
        content = subprocess.getoutput(f"gresource extract {gresource_file} {resource}")
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(file=filepath, mode="w+") as open_file:
            open_file.write(content)
    return TempExtractedDir

def extract_default_theme(name:str="default-extracted"):
    """extracts resources of the default theme and puts them in a structure so that
    they can be used as a gnome-shell/GDM theme"""

    source_shell_dir = extract_theme_from_gresource_file(gresource_file=get_default_gresource_file())
    target_theme_dir = f"{ThemesDir}/{name}"
    target_shell_dir = f"{target_theme_dir}/gnome-shell"
    elevated_commands_list.add(f"rm -rf {target_theme_dir}")
    elevated_commands_list.add(f"mkdir -p {target_theme_dir}")
    elevated_commands_list.add(f"mv -T {source_shell_dir} {target_shell_dir}")

def auto_backup():
    """backup the default theme's GResource file (only if needed)
    for its use as the 'default' theme"""

    default_gresource =  get_default_gresource_file()
    if default_gresource and default_gresource != GdmGresourceAutoBackup:
        print("saving default theme ...")
        elevated_commands_list.add(f"cp {default_gresource} {GdmGresourceAutoBackup}")

def backup_update():
    """update backup of the default theme's GResource file on demand
    for its use as a restore point for the 'default' theme"""

    default_gresource =  get_default_gresource_file()
    if default_gresource and default_gresource != GdmGresourceManualBackup:
        print("updating backup of default theme ...")
        elevated_commands_list.add(f"cp {default_gresource} {GdmGresourceManualBackup}")

def backup_restore():
    """restore the 'default' theme's GResource file from the manually created backup"""

    if  os.path.isfile(GdmGresourceManualBackup):
        print("restoring default theme from backup ...")
        elevated_commands_list.add(f"cp {GdmGresourceManualBackup} {GdmGresourceAutoBackup}")

def compile_theme(shellDir:str, additional_css:str):
    """Compile a theme into a GResource file for its use as the GDM theme"""

    # Remove temporary directory if already exists
    if os.path.exists(TempShellDir):
        shutil.rmtree(TempShellDir)
    tempGresourceFile = os.path.join(TempDir, 'gnome-shell-theme.gresource')
    # Remove temporary file if already exists
    if os.path.exists(tempGresourceFile):
        os.remove(tempGresourceFile)
    # Copy default resources to temporary directory
    shutil.copytree(extract_theme_from_gresource_file(get_default_gresource_file()), TempShellDir)
    # Copy gnome-shell dir of theme to temporary directory
    if shellDir:
        shutil.copytree(shellDir, TempShellDir, dirs_exist_ok=True)
    # Inject custom-theme identity
    open(os.path.join(TempShellDir, CustomThemeIdentity), 'w').close()
    # Background CSS
    with open(f"{TempShellDir}/gnome-shell.css", "a") as shell_css:
        print(additional_css, file=shell_css)
        pass
    
    # Copy gnome-shell.css to gdm.css and gdm3.css
    shutil.copy(src=f"{TempShellDir}/gnome-shell.css", dst=f"{TempShellDir}/gdm.css")
    shutil.copy(src=f"{TempShellDir}/gnome-shell.css", dst=f"{TempShellDir}/gdm3.css")

    # Open /tmp/gdm-settings/gnome-shell/gnome-shell-theme.gresource.xml for writing
    with open(os.path.join(TempShellDir, 'gnome-shell-theme.gresource.xml'), 'w') as GresourceXml:
        # Fill gnome-shell-theme.gresource.xml
        print('<?xml version="1.0" encoding="UTF-8"?>',
              '<gresources>',
              ' <gresource prefix="/org/gnome/shell/theme">',
              sep='\n',
              file=GresourceXml)
        for file in listdir_recursive(TempShellDir):
            print('  <file>' + file + '</file>', file=GresourceXml)
        print(' </gresource>',
              '</gresources>',
              sep='\n',
              file=GresourceXml)

    # Compile Theme
    os.system(f'glib-compile-resources --sourcedir={TempShellDir} {TempShellDir}/gnome-shell-theme.gresource.xml')
    shutil.move(os.path.join(TempShellDir,'gnome-shell-theme.gresource'), TempDir)
    shutil.rmtree(TempShellDir)
    return  tempGresourceFile
