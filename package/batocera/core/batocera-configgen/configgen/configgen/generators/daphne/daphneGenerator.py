#!/usr/bin/env python

import Command
import batoceraFiles
from generators.Generator import Generator
import shutil
import os
from . import daphneControllers

class DaphneGenerator(Generator):

    # Main entry of the module
    def generate(self, system, rom, playersControllers, gameResolution):
        if not os.path.exists(os.path.dirname(batoceraFiles.daphneConfig)):
            os.makedirs(os.path.dirname(batoceraFiles.daphneConfig))

        # controllers
        daphneControllers.generateControllerConfig(batoceraFiles.daphneConfig, playersControllers)

        # extension used .daphne and the file to start the game is in the folder .daphne with the extension .txt
        romName = os.path.splitext(os.path.basename(rom))[0]
        frameFile = rom + "/" + romName + ".txt"
        commandsFile = rom + "/" + romName + ".commands"
        singeFile = rom + "/" + romName + ".singe"

        if os.path.isfile(singeFile):
            commandArray = [batoceraFiles.batoceraBins[system.config['emulator']],
                            "singe", "vldp", "-retropath", "-framefile", frameFile, "-script", singeFile, "-fullscreen",
                            "-manymouse", "-datadir", batoceraFiles.daphneDatadir, "-homedir", batoceraFiles.daphneDatadir]
        else:
            commandArray = [batoceraFiles.batoceraBins[system.config['emulator']],
                            romName, "vldp", "-framefile", frameFile, "-useoverlaysb", "2", "-fullscreen",
                            "-fastboot", "-datadir", batoceraFiles.daphneDatadir, "-homedir", batoceraFiles.daphneHomedir]

        # Aspect ratio
        if system.config["ratio"] == "4/3":
            commandArray.append("-force_aspect_ratio")

        # Invert required when screen is rotated
        if gameResolution["width"] < gameResolution["height"]:
            commandArray.extend(["-x", str(gameResolution["height"]), "-y", str(gameResolution["width"])])
        else:
            commandArray.extend(["-x", str(gameResolution["width"]), "-y", str(gameResolution["height"])])


        # Disable Bilinear Filtering
        if system.isOptSet('bilinear_filter') and system.getOptBoolean("bilinear_filter"):
            commandArray.append("-nolinear_scale")

        # Blend Sprites (Singe)
        if system.isOptSet('blend_sprites') and system.getOptBoolean("blend_sprites"):
            commandArray.append("-blend_sprites")

        # Oversize Overlay (Singe) for HD lightgun games
        if system.isOptSet('lightgun_hd') and system.getOptBoolean("lightgun_hd"):
            commandArray.append("-oversize_overlay")

        # Invert Axis
        if system.isOptSet('invert_axis') and system.getOptBoolean("invert_axis"):
            commandArray.append("-tiphat")

        # The folder may have a file with the game name and .commands with extra arguments to run the game.
        if os.path.isfile(commandsFile):
            commandArray.extend(open(commandsFile,'r').read().split())

        return Command.Command(array=commandArray)

