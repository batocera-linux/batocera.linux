#!/usr/bin/env python

import Command
from generators.Generator import Generator
import controllersConfig
from shutil import copyfile
import os
import batoceraFiles
import filecmp
from distutils.dir_util import copy_tree

nba_file = "/usr/nba/NanoBoyAdvance"
nba_Config = "/usr/nba/"
nba_Homedir = batoceraFiles.CONF + "/nba"

class NbaGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):
        nba_exec = nba_Homedir + "/NanoBoyAdvance"
        shader_dir = nba_Homedir + "/shader"

        # Create Folder
        if not os.path.exists(nba_Homedir):
            os.makedirs(nba_Homedir)

        # Copy File Needed
        if not os.path.exists(shader_dir):
            copy_tree(nba_Config, nba_Homedir)

        if not os.path.exists(nba_exec) or not filecmp.cmp(nba_file, nba_exec):
            copyfile(nba_file, nba_exec)
            os.chmod(nba_exec, 0o0775)

        commandArray = [nba_exec, "--fullscreen", rom]
        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
            })
