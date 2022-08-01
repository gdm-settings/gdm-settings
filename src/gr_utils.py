''' Utilities (functions) for GResource files of GNOME Shell themes'''

import os
import logging
from . import env

ThemesDir                = env.HOST_DATA_DIRS[0]
CustomThemeIdentity      = 'custom-theme'
GdmUsername              = 'gdm'
ShellGresourceFile       = None
ShellGresourceAutoBackup = None
CustomGresourceFile      = None
UbuntuGdmGresourceFile   = None

for data_dir in env.HOST_DATA_DIRS:
    file = os.path.join (data_dir,  'gnome-shell', 'gnome-shell-theme.gresource')
    if os.path.isfile (env.HOST_ROOT + file):
        ShellGresourceFile       = file
        ShellGresourceAutoBackup = ShellGresourceFile + ".default"
        CustomGresourceFile      = ShellGresourceFile + ".gdm_settings"
        break

if 'ubuntu' in [env.OS_ID] + env.OS_ID_LIKE.split():
    from .utils import version
    if version(env.OS_VERSION_ID) >= version('21.10'):
        UbuntuGdmGresourceFile = '/usr/share/gnome-shell/gdm-theme.gresource'
    else:
        UbuntuGdmGresourceFile = '/usr/share/gnome-shell/gdm3-theme.gresource'
elif 'debian' in [env.OS_ID] + env.OS_ID_LIKE.split():
    GdmUsername = 'Debian-gdm'

logging.info(f"ShellGresourceFile     = {ShellGresourceFile}")
logging.info(f"UbuntuGdmGresourceFile = {UbuntuGdmGresourceFile}")

def is_unmodified(gresourceFile:str):
    """checks if the provided file is a GResource file of the default theme"""

    from .utils import getstdout

    if os.path.exists(gresourceFile):
        if getstdout(["gresource", "list", gresourceFile, "/org/gnome/shell/theme/gnome-shell.css"]):
            if not getstdout(f"gresource list {gresourceFile} /org/gnome/shell/theme/{CustomThemeIdentity}"):
                return True
    return False

def get_default() -> str:
    """get full path to the unmodified GResource file of the default theme (if the file exists)"""

    for file in ShellGresourceFile, ShellGresourceAutoBackup:
       if is_unmodified(env.HOST_ROOT + file):
           return file

def extract_default_theme(destination:str, /):
    '''Extract default GNOME Shell theme'''

    from os import makedirs
    from .utils import getstdout

    if os.path.exists(destination):
        from shutil import rmtree
        rmtree(destination)

    destination_shell_dir = os.path.join(destination, 'gnome-shell')
    gresource_file = get_default()
    resource_list = getstdout(["gresource", "list", gresource_file]).decode().splitlines()

    if not gresource_file:
        raise FileNotFoundError('No unmodified GResource file of the default shell theme was found')

    for resource in resource_list:
        filename = resource.removeprefix("/org/gnome/shell/theme/")
        filepath = os.path.join(destination_shell_dir, filename)
        content  = getstdout(["gresource", "extract", env.HOST_ROOT + gresource_file, resource])

        makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, "wb") as opened_file:
            opened_file.write(content)

class BackgroundImageNotFoundError (FileNotFoundError): pass

def compile(shellDir:str, additional_css:str, background_image:str=''):
    """Compile a theme into a GResource file for its use as a GDM theme"""

    from os import remove
    from shutil import copy, copytree, rmtree

    temp_gresource_file = os.path.join(env.TEMP_DIR, 'gnome-shell-theme.gresource')
    temp_theme_dir = os.path.join(env.TEMP_DIR, 'extracted-theme')
    temp_shell_dir = os.path.join(temp_theme_dir, 'gnome-shell')

    # Remove temporary directory if already exists
    if os.path.exists(temp_theme_dir):
        rmtree(temp_theme_dir)

    # Remove temporary file if already exists
    if os.path.exists(temp_gresource_file):
        remove(temp_gresource_file)

    # Copy default resources to temporary directory
    extract_default_theme(temp_theme_dir)

    # Copy gnome-shell dir of theme to temporary directory
    if shellDir:
        copytree(shellDir, temp_shell_dir, dirs_exist_ok=True)

    # Inject custom-theme identity
    open(os.path.join(temp_shell_dir, CustomThemeIdentity), 'w').close()

    # Background Image
    if background_image:
        if os.path.isfile(background_image):
            copy(background_image, os.path.join(temp_shell_dir, 'background'))
        else:
            raise BackgroundImageNotFoundError(2, 'No such file', background_image)

    # Additional CSS
    with open(f"{temp_shell_dir}/gnome-shell.css", "a") as shell_css:
        print(additional_css, file=shell_css)

    # Copy gnome-shell.css to gdm.css and gdm3.css
    copy(f"{temp_shell_dir}/gnome-shell.css", f"{temp_shell_dir}/gdm.css")
    copy(f"{temp_shell_dir}/gnome-shell.css", f"{temp_shell_dir}/gdm3.css")

    # Get a list of all files in the shell theme
    # Note: We do this before calling open() so as not to include .gresource.xml file itself in the list
    from .utils import listdir_recursive
    file_list = listdir_recursive(temp_shell_dir)

    gresource_xml_filename = os.path.join(temp_shell_dir, 'gnome-shell-theme.gresource.xml')

    # Create gnome-shell-theme.gresource.xml file
    with open(gresource_xml_filename, 'w') as GresourceXml:
        print('<?xml version="1.0" encoding="UTF-8"?>',
              '<gresources>',
              ' <gresource prefix="/org/gnome/shell/theme">',
            *('  <file>'+file+'</file>' for file in file_list),
              ' </gresource>',
              '</gresources>',

              sep='\n',
              file=GresourceXml,
             )

    # Compile Theme
    from subprocess import run
    run(['glib-compile-resources',
         '--sourcedir', temp_shell_dir,
         '--target', temp_gresource_file,
         gresource_xml_filename,
       ])

    # Return path to the generated GResource file
    return  temp_gresource_file
