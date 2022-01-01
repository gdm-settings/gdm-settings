#!/bin/python
'''Functions to be used by this project'''

import os, glob, magic, re, shutil, subprocess
from variables import *

class ElevatedCommandsList:
    """ Holds a list of commands to run with elevated privilages """
    def __init__(self) -> None:
        self.__list = []
        self.__shebang = "#!/bin/sh"
        self.__elevator = "pkexec"

    def shebang(self, shebang:str=None):
        """ Shebang to determine shell for running elevated commands """
        if shebang:
            self.__shebang = shebang
        else:
            return self.__shebang

    def elevator(self, elevator:str=None):
        """
        Program to use for privilage elevation 
        
        Example: "sudo", "doas", "pkexec", etc.
        """
        if elevator:
            self.__elevator = elevator
        else:
            return self.__elevator

    def add(self, cmd:str):
        """ Add a new command to the list """
        self.__list.append(cmd)

    def clear(self):
        """ Clear command list """
        self.__list.clear()

    def run_only(self):
        """ Run commands but DO NOT clear command list """
        if len(self.__list):
            os.makedirs(name=TempDir, exist_ok=True)
            script_file = f"{TempDir}/run-elevated"
            with open(script_file, "w") as open_script_file:
                print(self.__shebang, *self.__list, sep="\n", file=open_script_file)
            os.chmod(path=script_file, mode=755)
            subprocess.run(args=[self.__elevator, script_file])
            os.remove(script_file)

    def run(self):
        """ Run commands and clear command list"""
        self.run_only()
        self.clear()

elevated_commands_list = ElevatedCommandsList()

def get_theme_list():
    List=['default']
    for dir in sorted(glob.glob('/usr/share/themes/*'), key=str.casefold):
        if os.path.isfile(dir + "/gnome-shell/gnome-shell.css"):
            List.append(os.path.basename(dir))
    return List

def is_default_gresource(gresourceFile:str):
    if os.path.exists(gresourceFile):
        if subprocess.getoutput(f"gresource list {gresourceFile} /org/gnome/shell/theme/gnome-shell.css"):
            if not subprocess.getoutput(f"gresource list {gresourceFile} /org/gnome/shell/theme/{CustomThemeIdentity}"):
                return True
    return False

def get_default_gresource() -> str:
    for file in GdmGresourceFile, GdmGresourceAutoBackup, GdmGresourceManualBackup:
       if is_default_gresource(file):
           return file

def auto_backup():
    default_gresource =  get_default_gresource()
    if default_gresource and default_gresource != GdmGresourceAutoBackup:
        print("saving default theme ...")
        elevated_commands_list.add(f"cp {default_gresource} {GdmGresourceAutoBackup}")

def extract_theme_from_gresource(gresource_file:str):
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
    # Remove temporary directory if already exists
    if os.path.exists(TempShellDir):
        shutil.rmtree(TempShellDir)
    # Copy gnome-shell dir of theme to temporary directory
    shutil.copytree(shellDir, TempShellDir)
    # Inject custom-theme identity
    open(os.path.join(TempShellDir, CustomThemeIdentity), 'w').close()
    # Background CSS
    bgr_css_lines=["",
                   "#lockDialogGroup {",
                  f"  background-image: url('file://{GdmBackground}');",
                   "  background-size: cover;",
                   "  background-repeat: no-repeat;",
                   "  background-attachment: fixed;",
                   "  background-position: center;",
                   "}"]

    # Open gnome-shell.css for appending
    shell_css = open(f"{TempShellDir}/gnome-shell.css", "a")
    # Inject Background CSS
    if os.path.isfile(GdmBackground):
        print(*bgr_css_lines, sep='\n', file=shell_css)
    # Inject User-Provided Custom CSS
    if os.path.isfile(CustomCss):
        with open(CustomCss, "r") as CustomCssContent:
            shell_css.write(CustomCssContent.read())
    # Close gnome-shell.css
    shell_css.close()
    
    # Copy gnome-shell.css to gdm.css and gdm3.css
    shutil.copy(src=f"{TempShellDir}/gnome-shell.css", dst=f"{TempShellDir}/gdm.css")
    shutil.copy(src=f"{TempShellDir}/gnome-shell.css", dst=f"{TempShellDir}/gdm3.css")

    # Open /tmp/gdm-settings/gnome-shell/gnome-shell-theme.gresource.xml for writing
    GresourceXml = os.path.join(TempShellDir, 'gnome-shell-theme.gresource.xml')
    GresourceXmlWrite = open(GresourceXml, 'w')

    # Fill gnome-shell-theme.gresource.xml
    GresourceXmlWrite.writelines(['<?xml version="1.0" encoding="UTF-8"?>',
                            '<gresources>',
                            ' <gresource prefix="/org/gnome/shell/theme">'])
    for file in listdir_recursive(TempShellDir):
        GresourceXmlWrite.write('  <file>' + file + '</file>')
    GresourceXmlWrite.writelines([' </gresource>',
                            '</gresources>'])
    GresourceXmlWrite.close()

    # Compile Theme
    os.system(f'glib-compile-resources --sourcedir={TempShellDir} {TempShellDir}/gnome-shell-theme.gresource.xml')
    shutil.move(os.path.join(TempShellDir,'gnome-shell-theme.gresource'), TempDir)
    shutil.rmtree(TempShellDir)
    return  os.path.join(TempDir,'gnome-shell-theme.gresource')

def set_background(background:str):
    if background == 'none':
        print('remove background')
    elif background in AcceptableColors:
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

def set_theme(theme:str):
    auto_backup()
    os.makedirs(TempDir, exist_ok=True)
    print(f"applying theme '{theme}' ...")
    if theme == "default":
        shelldir = extract_theme_from_gresource(get_default_gresource())
    else:
        shelldir = f"/usr/share/themes/{theme}/gnome-shell"
    compiled_file = compile_theme(shellDir=shelldir)
    elevated_commands_list.add(f'mv {compiled_file} {GdmGresourceFile}')
    
def print_theme_list():
    print(*get_theme_list(), sep='\n')

def print_color_list():
    print(*AcceptableColors, sep='\n')

def backup_update():
    default_gresource =  get_default_gresource()
    if default_gresource and default_gresource != GdmGresourceManualBackup:
        print("updating backup of default theme ...")
        elevated_commands_list.add(f"cp {default_gresource} {GdmGresourceManualBackup}")

def backup_restore():
    if  os.path.isfile(GdmGresourceManualBackup):
        print("restoring default theme from backup ...")
        elevated_commands_list.add(f"cp {GdmGresourceManualBackup} {GdmGresourceAutoBackup}")

def extract_default_theme(name:str="default-extracted"):
    source_shell_dir = extract_theme_from_gresource(gresource_file=get_default_gresource())
    target_theme_dir = f"{ThemesDir}/{name}"
    target_shell_dir = f"{target_theme_dir}/gnome-shell"
    elevated_commands_list.add(f"rm -rf {target_theme_dir}")
    elevated_commands_list.add(f"mkdir -p {target_theme_dir}")
    elevated_commands_list.add(f"mv -T {source_shell_dir} {target_shell_dir}")

def show_manual(progName:str):
    os.system('man ' + progName)

def show_examples(progName:str):
    print('show examples')
