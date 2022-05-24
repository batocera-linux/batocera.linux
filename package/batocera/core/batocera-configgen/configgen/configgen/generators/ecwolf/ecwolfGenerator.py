#!/usr/bin/env python

import Command
import batoceraFiles
from generators.Generator import Generator
import controllersConfig
import os
from os import path
import codecs

ecwolfConfig = batoceraFiles.CONF + "/ecwolf"
ecwolfConfigDir = "/userdata/system/.config/ecwolf"
ecwolfConfigSrc = "/userdata/system/.config/ecwolf/ecwolf.cfg"
ecwolfConfigDest = batoceraFiles.CONF + "/ecwolf/ecwolf.cfg"
ecwolfSaves = batoceraFiles.SAVES + "/ecwolf"

class ECWolfGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):
        # Create config folders
        if not path.isdir(ecwolfConfig):
            os.mkdir(ecwolfConfig)
        if not path.isdir(ecwolfConfigDir):
            os.mkdir(ecwolfConfigDir)
        # Create config file if not there
        if not path.isfile(ecwolfConfigSrc):
            f = codecs.open(ecwolfConfigSrc, "x")
            f.write('Vid_FullScreen = 1;\n')
            f.write('Vid_Aspect = 0;\n')
            f.write('Vid_Vsync = 1;\n')
            f.write('FullScreenWidth = {};\n'.format(gameResolution["width"]))
            f.write('FullScreenHeight = {};\n'.format(gameResolution["height"]))
            f.close()
        
        # Symbolic link the cfg file
        if not path.exists(ecwolfConfigDest):
            os.symlink(ecwolfConfigSrc, ecwolfConfigDest)
        
        # Set the resolution
        if path.isfile(ecwolfConfigDest):
            f = codecs.open(ecwolfConfigDest, "w")
            f.write('Vid_FullScreen = 1;\n')
            f.write('Vid_Aspect = 0;\n')
            f.write('Vid_Vsync = 1;\n')
            f.write('FullScreenWidth = {};\n'.format(gameResolution["width"]))
            f.write('FullScreenHeight = {};\n'.format(gameResolution["height"]))
            f.close()
        
        # Create save folder
        if not path.isdir(ecwolfSaves):
            os.mkdir(ecwolfSaves)

        try:
            os.chdir(rom)
        # Only game directories, not .zip
        except Exception as e:
            print("Error: couldn't go into directory {} ({})".format(rom, e))
        commandArray = ["ecwolf", "--joystick", "--savedir '/userdata/saves/ecwolf'"]
        return Command.Command(array=commandArray)
