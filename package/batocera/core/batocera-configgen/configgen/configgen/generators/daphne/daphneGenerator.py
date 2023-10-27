#!/usr/bin/env python

import Command
import batoceraFiles
from generators.Generator import Generator
import shutil
import os
import controllersConfig
import filecmp
from utils.logger import get_logger

eslog = get_logger(__name__)

class DaphneGenerator(Generator):

    # Main entry of the module
    def generate(self, system, rom, playersControllers, guns, wheels, gameResolution):
        # copy input.ini file templates
        daphneConfigSource = "/usr/share/daphne/hypinput_gamepad.ini"

        if not os.path.isdir(batoceraFiles.daphneDatadir):
            os.mkdir(batoceraFiles.daphneDatadir)
        if not os.path.exists(batoceraFiles.daphneConfig) or not filecmp.cmp(daphneConfigSource, batoceraFiles.daphneConfig):
            shutil.copyfile(daphneConfigSource, batoceraFiles.daphneConfig)

        # create a custom ini
        if not os.path.exists(batoceraFiles.daphneDatadir + "/custom.ini"):
            shutil.copyfile(batoceraFiles.daphneConfig, batoceraFiles.daphneDatadir + "/custom.ini")
            
        # copy required resources to userdata config folder as needed
        def copy_resources(source_dir, destination_dir):
            if not os.path.exists(destination_dir):
                shutil.copytree(source_dir, destination_dir)
            else:
                for item in os.listdir(source_dir):
                    source_item = os.path.join(source_dir, item)
                    destination_item = os.path.join(destination_dir, item)
                    if os.path.isfile(source_item):
                        if not os.path.exists(destination_item) or os.path.getmtime(source_item) > os.path.getmtime(destination_item):
                            shutil.copy2(source_item, destination_dir)
                        elif os.path.isdir(source_item):
                            copy_resources(source_item, destination_item)
        
        directories = [
            {"source": "/usr/share/daphne/pics", "destination": batoceraFiles.daphneDatadir + "/pics"},
            {"source": "/usr/share/daphne/sound", "destination": batoceraFiles.daphneDatadir + "/sound"},
            {"source": "/usr/share/daphne/fonts", "destination": batoceraFiles.daphneDatadir + "/fonts"}
        ]

        # Copy/update directories
        for directory in directories:
            copy_resources(directory["source"], directory["destination"])
        
        # create symbolic link for singe
        if not os.path.exists(batoceraFiles.daphneDatadir + "/singe"):
            os.mkdir(batoceraFiles.daphneDatadir + "/singe")
            if not os.path.exists(batoceraFiles.daphneHomedir + "/roms"):
                os.mkdir(batoceraFiles.daphneHomedir + "/roms")
            os.symlink(batoceraFiles.daphneHomedir + "/roms", batoceraFiles.daphneDatadir + "/singe")
        if not os.path.islink(batoceraFiles.daphneDatadir + "/singe"):
            eslog.error("Your {} directory isn't a symlink, that's not good.".format(batoceraFiles.daphneDatadir + "/singe"))
                
        # extension used .daphne and the file to start the game is in the folder .daphne with the extension .txt
        romName = os.path.splitext(os.path.basename(rom))[0]
        frameFile = rom + "/" + romName + ".txt"
        commandsFile = rom + "/" + romName + ".commands"
        singeFile = rom + "/" + romName + ".singe"

        if os.path.isfile(singeFile):
            commandArray = [batoceraFiles.batoceraBins[system.config['emulator']],
                            "singe", "vldp", "-retropath", "-framefile", frameFile, "-script", singeFile, "-fullscreen",
                            "-gamepad", "-datadir", batoceraFiles.daphneDatadir, "-homedir", batoceraFiles.daphneDatadir]
        else:
            commandArray = [batoceraFiles.batoceraBins[system.config['emulator']],
                            romName, "vldp", "-framefile", frameFile, "-fullscreen",
                            "-fastboot", "-gamepad", "-datadir", batoceraFiles.daphneDatadir, "-homedir", batoceraFiles.daphneHomedir]
        
        # controller config file
        if system.isOptSet('daphne_joy')  and system.getOptBoolean('daphne_joy'):
            commandArray.extend(['-keymapfile', 'custom.ini'])
        else:
            commandArray.extend(["-keymapfile", batoceraFiles.daphneConfigfile])

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

        # Enable Bilinear Filtering
        if system.isOptSet('bilinear_filter') and system.getOptBoolean("bilinear_filter"):
            commandArray.append("-linear_scale")

        #The following options should only be set when os.path.isfile(singeFile) is true.
        #-blend_sprites, -nocrosshair, -sinden or -manymouse
        if os.path.isfile(singeFile):
            # Blend Sprites (Singe)
            if system.isOptSet('blend_sprites') and system.getOptBoolean("blend_sprites"):
                commandArray.append("-blend_sprites")

            bordersSize = controllersConfig.gunsBordersSizeName(guns, system.config)
            if bordersSize is not None:

                borderColor = "w"
                if "controllers.guns.borderscolor" in system.config:
                    borderColorOpt = system.config["controllers.guns.borderscolor"]
                    if borderColorOpt == "white":
                        borderColor = "w"
                    elif borderColorOpt == "red":
                        borderColor = "r"
                    elif borderColorOpt == "green":
                        borderColor = "g"
                    elif borderColorOpt == "blue":
                        borderColor = "b"

                if bordersSize == "thin":
                    commandArray.extend(["-sinden", "2", borderColor])
                elif bordersSize == "medium":
                    commandArray.extend(["-sinden", "4", borderColor])
                else:
                    commandArray.extend(["-sinden", "6", borderColor])
            else:
                if len(guns) > 0: # enable manymouse for guns
                    commandArray.extend(["-manymouse"]) # sinden implies manymouse
                else:
                    if system.isOptSet('abs_mouse_input') and system.getOptBoolean("abs_mouse_input"):
                        commandArray.extend(["-manymouse"]) # this is causing issues on some "non-gun" games

            # crosshair
            if system.isOptSet('daphne_crosshair'):
                if not system.getOptBoolean("daphne_crosshair"):
                    commandArray.append("-nocrosshair")
                else:
                    if not controllersConfig.gunsNeedCrosses(guns):
                        commandArray.append("-nocrosshair")

        # Invert HAT Axis
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

        # Hide crosshair in supported games (e.g. ActionMax, ALG)
        if system.isOptSet('singe_crosshair') and system.getOptBoolean("singe_crosshair"):
            commandArray.append("-nocrosshair")

        # Enable SDL_TEXTUREACCESS_STREAMING, can aid SBC's with SDL2 => 2.0.16
        if system.isOptSet('daphne_texturestream') and system.getOptBoolean("daphne_texturestream"):
            commandArray.append("-texturestream") 
            
        # The folder may have a file with the game name and .commands with extra arguments to run the game.
        if os.path.isfile(commandsFile):
            commandArray.extend(open(commandsFile,'r').read().split())

        # We now use SDL controller config
        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers),
                'SDL_JOYSTICK_HIDAPI': '0'
            }
        )
    
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
