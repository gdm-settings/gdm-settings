''' Utilities (functions) for GResource files of GNOME Shell themes'''

import os
import shutil
import subprocess

from gdms import env
from gdms import utils


ThemesDir              = os.path.join(env.HOST_DATA_DIRS[0], 'themes')
CustomThemeIdentity    = 'custom-theme'
GdmUsername            = 'gdm'
ShellGresourceFile     = None
DefaultGresourceFile   = None
CustomGresourceFile    = None
UbuntuGdmGresourceFile = None

for data_dir in env.HOST_DATA_DIRS:
    file = os.path.join (data_dir,  'gnome-shell', 'gnome-shell-theme.gresource')
    if os.path.isfile (env.HOST_ROOT + file):
        ShellGresourceFile   = file
        DefaultGresourceFile = ShellGresourceFile + ".default"
        CustomGresourceFile  = ShellGresourceFile + ".gdm_settings"
        break

if 'ubuntu' in env.OS_IDs:
    if os.path.exists(env.HOST_ROOT+'/usr/share/gnome-shell/gdm-theme.gresource'):
        UbuntuGdmGresourceFile = '/usr/share/gnome-shell/gdm-theme.gresource'
    else:
        UbuntuGdmGresourceFile = '/usr/share/gnome-shell/gdm3-theme.gresource'

with open(env.HOST_ROOT+'/etc/passwd') as passwd_db:
    for line in passwd_db:
        if line.startswith('Debian-gdm'):
            GdmUsername = 'Debian-gdm'
            break


def is_unmodified(gresourceFile:str):
    """checks if the provided file is a GResource file of the default theme"""

    if env.HOST_ROOT and not gresourceFile.startswith(env.HOST_ROOT):
        gresourceFile = env.HOST_ROOT + gresourceFile

    if os.path.exists(gresourceFile):
        if utils.get_stdout(["gresource", "list", gresourceFile, "/org/gnome/shell/theme/gnome-shell.css"]):
            if not utils.get_stdout(f"gresource list {gresourceFile} /org/gnome/shell/theme/{CustomThemeIdentity}"):
                return True
    return False

def get_default() -> str:
    """get full path to the unmodified GResource file of the default theme (if the file exists)"""

    for file in ShellGresourceFile, DefaultGresourceFile:
       if is_unmodified(file):
           return file

def extract_default_theme(destination:str, /):
    '''Extract default GNOME Shell theme'''

    if os.path.exists(destination):
        shutil.rmtree(destination)

    destination_shell_dir = os.path.join(destination, 'gnome-shell')
    gresource_file = get_default()
    resource_list = utils.get_stdout(["gresource", "list", env.HOST_ROOT + gresource_file]).splitlines()

    if not gresource_file:
        raise FileNotFoundError('No unmodified GResource file of the default shell theme was found')

    for resource in resource_list:
        filename = resource.removeprefix("/org/gnome/shell/theme/")
        filepath = os.path.join(destination_shell_dir, filename)
        content  = utils.get_stdout(["gresource", "extract", env.HOST_ROOT + gresource_file, resource],
                                  decode=False)

        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, "wb") as opened_file:
            opened_file.write(content)

class BackgroundImageNotFoundError (FileNotFoundError): pass

def compile(shellDir:str, additional_css:str, background_image:str=''):
    """Compile a theme into a GResource file for its use as a GDM theme"""

    temp_gresource_file = os.path.join(env.TEMP_DIR, 'gnome-shell-theme.gresource')
    temp_gresource_xml = f'{temp_gresource_file}.xml'
    temp_theme_dir = os.path.join(env.TEMP_DIR, 'temp-theme')
    temp_shell_dir = os.path.join(temp_theme_dir, 'gnome-shell')

    if os.path.exists(temp_theme_dir):
        shutil.rmtree(temp_theme_dir)

    if os.path.exists(temp_gresource_file):
        os.remove(temp_gresource_file)

    extract_default_theme(temp_theme_dir)

    if shellDir:
        css_files = {}
        for filename in os.listdir(temp_shell_dir):
            if not filename.endswith('.css'):
                continue
            with open(os.path.join(temp_shell_dir, filename)) as file_io:
                css_files[filename] = file_io.read()

        shutil.copytree(shellDir, temp_shell_dir, dirs_exist_ok=True)

        for filename, contents_default in css_files.items():
            if not os.path.isfile(os.path.join(shellDir, filename)):
                continue
            with open(os.path.join(shellDir, filename)) as file_io:
                contents_theme = file_io.read()
            with open(os.path.join(temp_shell_dir, filename), 'w') as file_io:
                contents = contents_default + '\n\n' + contents_theme
                file_io.write(contents)

    # Inject custom-theme identity
    open(os.path.join(temp_shell_dir, CustomThemeIdentity), 'w').close()

    if background_image:
        if os.path.isfile(background_image):
            shutil.copy(background_image, os.path.join(temp_shell_dir, 'background'))
        else:
            raise BackgroundImageNotFoundError(2, 'No such file', background_image)

    with open(f"{temp_shell_dir}/gnome-shell.css", "a") as shell_css:
        shell_css.write(additional_css)

    shutil.copy(f"{temp_shell_dir}/gnome-shell.css", f"{temp_shell_dir}/gdm.css")
    shutil.copy(f"{temp_shell_dir}/gnome-shell.css", f"{temp_shell_dir}/gdm3.css")

    with open(temp_gresource_xml, 'w') as GresourceXml:
        print('<?xml version="1.0" encoding="UTF-8"?>',
              '<gresources>',
              ' <gresource prefix="/org/gnome/shell/theme">',
            *('  <file>'+file+'</file>' for file in utils.list_files(temp_shell_dir)),
              ' </gresource>',
              '</gresources>',

              sep='\n',
              file=GresourceXml,
             )

    # Compile Theme
    subprocess.run(['glib-compile-resources',
         '--sourcedir', temp_shell_dir,
         '--target', temp_gresource_file,
         temp_gresource_xml,
       ])

    # Return path to the generated GResource file
    return  temp_gresource_file
