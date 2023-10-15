#!/usr/bin/env python

import Command
import batoceraFiles
from generators.Generator import Generator
import controllersConfig
import os
from os import path
import codecs

class ECWolfGenerator(Generator):

    def generate(self, system, rom, playersControllers, guns, wheels, gameResolution):

        ecwolfConfigDir = batoceraFiles.CONF + "/ecwolf"
        ecwolfConfigFile = ecwolfConfigDir + "/ecwolf.cfg"
        ecwolfSaves = batoceraFiles.SAVES + "/ecwolf/" + path.basename(rom)
        ecwolfArray = ["ecwolf"] # Binary for command array

        # Create config folders
        if not path.isdir(ecwolfConfigDir):
            os.mkdir(ecwolfConfigDir)
        # Create config file if not there
        if not path.isfile(ecwolfConfigFile):
            f = codecs.open(ecwolfConfigFile, "x")
            f.write('Vid_FullScreen = 1;\n')
            f.write('Vid_Aspect = 0;\n')
            f.write('Vid_Vsync = 1;\n')
            f.write('QuitOnEscape = 1;\n')
            f.write('FullScreenWidth = {};\n'.format(gameResolution["width"]))
            f.write('FullScreenHeight = {};\n'.format(gameResolution["height"]))
            f.close()
        
        # Set the resolution and some other defaults
        if path.isfile(ecwolfConfigFile):
            #We ignore some options in default config with py-dictonary...
            IgnoreConfigKeys = {"FullScreenWidth", "FullScreenHeight", "JoystickEnabled"}
            with codecs.open(ecwolfConfigFile, "r") as f:
                lines = {line for line in f}

            # ... write all the non ignored keys back to config file ...
            with codecs.open(ecwolfConfigFile, "w") as f:
                for line in lines:
                    if not IgnoreConfigKeys.intersection(line.split()):
                        f.write(line)
 
            # ... and append the ignored keys with default values now ;)
            f = codecs.open(ecwolfConfigFile, "a")
            f.write('JoystickEnabled = 1;\n')
            f.write('FullScreenWidth = {};\n'.format(gameResolution["width"]))
            f.write('FullScreenHeight = {};\n'.format(gameResolution["height"]))
            f.close()

        # Create save folder, according rom name with extension
        if not path.isdir(ecwolfSaves):
            os.mkdir(ecwolfSaves)

        # Use the directory method with ecwolf extension and datafiles (wl6 or sod or nh3) inside
        if path.isdir(rom):
            try:
                os.chdir(rom)
            # Only game directories, not .ecwolf or .pk3 files
            except Exception as e:
                print(f"Error: couldn't go into directory {rom} ({e})")

        # File method .ecwolf (recommended) for command parameters, first argument is path to dataset, next parameters according ecwolf --help
        # File method .pk3, put pk3 files next to wl6 dataset and start the mod in ES
        if path.isfile(rom):
            os.chdir(path.dirname(rom))
            fextension = (path.splitext(rom)[1]).lower()

            if fextension == ".ecwolf":
                f = codecs.open(rom,"r")
                ecwolfArray += (f.readline().split())
                f.close()

                # If 1. parameter isn't an argument then assume it's a path
                if not "--" in ecwolfArray[1]:
                    try:
                        os.chdir(ecwolfArray[1])
                    except Exception as e:
                        print(f"Error: couldn't go into directory {ecwolfArray[1]} ({e})")
                    ecwolfArray.pop(1)

            if fextension == ".pk3":
                ecwolfArray += ["--file", path.basename(rom)]
 
        ecwolfArray += [
                 #Use values according ecwolf --help, do not miss any parameter  
                 "--savedir", ecwolfSaves
        ]

        return Command.Command(
             ecwolfArray,
             env={
                'XDG_CONFIG_HOME': batoceraFiles.CONF,
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
            }
        )
