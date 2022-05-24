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

        # Default -fullscreen behaviour respects game aspect ratio
        if system.isOptSet('daphne_ratio') and system.config['daphne_ratio'] == "stretch":
            commandArray.extend(["-x", str(gameResolution["width"]), "-y", str(gameResolution["height"])])
        elif system.isOptSet('daphne_ratio') and system.config['daphne_ratio'] == "force_ratio":
            commandArray.extend(["-force_aspect_ratio"])

        # Backend - Default OpenGL
        if system.isOptSet("gfxbackend") and system.config["gfxbackend"] == 'Vulkan':
            commandArray.append("-vulkan")
        else:
            commandArray.append("-opengl")

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

        # Game rotation options for vertical screens, default is 0.
        if system.isOptSet('daphne_rotate') and system.config['daphne_rotate'] == "90":
            commandArray.extend(["-rotate", "90"])
        elif system.isOptSet('daphne_rotate') and system.config['daphne_rotate'] == "270":
            commandArray.extend(["-rotate", "270"])

        # Singe joystick sensitivity, default is 5.
        if os.path.isfile(singeFile) and system.isOptSet('singe_joystick_range') and system.config['singe_joystick_range'] == "10":
            commandArray.extend(["-js_range", "10"])
        elif os.path.isfile(singeFile) and system.isOptSet('singe_joystick_range') and system.config['singe_joystick_range'] == "15":
            commandArray.extend(["-js_range", "15"])
        elif os.path.isfile(singeFile) and system.isOptSet('singe_joystick_range') and system.config['singe_joystick_range'] == "20":
            commandArray.extend(["-js_range", "20"])

        # Scanlines
        if system.isOptSet('daphne_scanlines') and system.getOptBoolean("daphne_scanlines"):
            commandArray.append("-scanlines")

        # Hide crosshair in supported games (e.g. ActionMax)
        if system.isOptSet('singe_crosshair') and system.getOptBoolean("singe_crosshair"):
            commandArray.append("-nocrosshair")

        # Enable SDL_TEXTUREACCESS_STREAMING, can aid SBC's with SDL2 => 2.0.16
        if system.isOptSet('daphne_texturestream') and system.getOptBoolean("daphne_texturestream"):
            commandArray.append("-texturestream") 
            
        # The folder may have a file with the game name and .commands with extra arguments to run the game.
        if os.path.isfile(commandsFile):
            commandArray.extend(open(commandsFile,'r').read().split())

        return Command.Command(array=commandArray)

    def getInGameRatio(self, config, gameResolution, rom):
        romName = os.path.splitext(os.path.basename(rom))[0]        
        singeFile = rom + "/" + romName + ".singe"
        if "daphne_ratio" in config:
            if config['daphne_ratio'] == "stretch":
                return 16/9
        if os.path.isfile(singeFile):
            return 16/9
        else:
            return 4/3
