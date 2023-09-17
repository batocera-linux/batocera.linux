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

    def generate(self, system, rom, playersControllers, guns, wheels, gameResolution):
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
            f.write('QuitOnEscape = 1;\n')
            f.write('FullScreenWidth = {};\n'.format(gameResolution["width"]))
            f.write('FullScreenHeight = {};\n'.format(gameResolution["height"]))
            f.close()

        # Create save folder
        if not path.isdir(ecwolfSaves):
            os.mkdir(ecwolfSaves)

        # Use the directory method with ecwolf extension and datafiles (wl6 or sod or nh3) inside
        if os.path.isdir(rom):
            try:
                os.chdir(rom)
            # Only game directories, not .ecwolf or .pk3 files
            except Exception as e:
                print(f"Error: couldn't go into directory {rom} ({e})")
            return Command.Command(
                array=[
                    'ecwolf',
                    # Command must be filled with arguments according ecwolf help page
                    "--savedir", ecwolfSaves,
                ],
                env={
                    'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
                }
            )

        # File method, .ecwolf (recommended) for command parameters, first argument is path to dataset, next parameters according ecwolf --help
        # Example 1.ecwolf: ./wolf3d --data wl6 --config /userdata/system/configs/ecwolf/mywolf.cfg
        # Example 2.ecwolf: ./wolf3d --data wl6 --file  ../HD/ECWolf_hdpack.pk3 ./HD/ECWolf_hdmus_3DO.pk3
        # File method .pk3, put pk3 files next to wl6 dataset and start the mod in ES
        # the pk3 method fails if the mod needs additional pk3 (see example 2)
        if os.path.isfile(rom):
            os.chdir(os.path.dirname(rom))
            fextension = (os.path.splitext(rom)[1]).lower()

            if fextension == ".ecwolf":
                f = open(rom,'r')
                array=(f.readline().split())
                f.close()

                # If 1. parameter isn't an argument then assume it's a path
                if not "--" in array[0]:
                    try:
                        os.chdir(array[0])
                    except Exception as e:
                        print(f"Error: couldn't go into directory {array[0]} ({e})")
                    array.pop(0)

            if fextension == ".pk3":
                array = ["--file", os.path.basename(rom)]

            # Here we add the binary first and some additional parameters
            array.insert(0, "ecwolf")
            array += ["--savedir", ecwolfSaves]
            return Command.Command(
                 array,
                 env={
                     'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)

                }
            )
