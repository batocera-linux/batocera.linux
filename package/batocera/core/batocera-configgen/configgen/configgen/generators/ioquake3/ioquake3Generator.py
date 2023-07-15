#!/usr/bin/env python
import Command
import batoceraFiles
from generators.Generator import Generator
import shutil
import os.path
import configparser
import controllersConfig
from shutil import copyfile
from . import ioquake3Config

class IOQuake3Generator(Generator):

    def generate(self, system, rom, playersControllers, guns, gameResolution):
        ioquake3Config.writeCfgFiles(system, rom, playersControllers, gameResolution)

        # ioquake3 looks for folder either in config or from where it's launched
        source_dir = "/usr/bin/ioquake3"
        destination_dir = "/userdata/roms/quake3"
        destination_file = os.path.join(destination_dir, "ioquake3")
        source_file = os.path.join(source_dir, "ioquake3")
        # therefore copy latest files to rom directory
        if not os.path.isfile(destination_file) or os.path.getmtime(source_file) > os.path.getmtime(destination_file):
            for file_name in os.listdir(source_dir):
                source_file = os.path.join(source_dir, file_name)
                destination_file = os.path.join(destination_dir, file_name)
                shutil.copy2(source_file, destination_file)
                
        # run from the rom directory
        commandArray = ["/userdata/roms/quake3/ioquake3", rom]

        environment = {
            "SDL_GAMECONTROLLERCONFIG": controllersConfig.generateSdlGameControllerConfig(playersControllers)
        }

        return Command.Command(array=commandArray, env=environment)

    def getInGameRatio(self, config, gameResolution, rom):
        if gameResolution["width"] / float(gameResolution["height"]) > ((16.0 / 9.0) - 0.1):
            return 16/9
        return 4/3
