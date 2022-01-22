import os
import subprocess

from info import *


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
