#!/usr/bin/env python

import Command
import batoceraFiles
from generators.Generator import Generator
import shutil
import os
import controllersConfig
import filecmp
import cv2
from utils.logger import get_logger

eslog = get_logger(__name__)

class HypseusSingeGenerator(Generator):

    @staticmethod
    def find_m2v_from_txt(txt_file):
        with open(txt_file, 'r') as file:
            for line in file:
                parts = line.strip().split()
                if parts:
                    filename = parts[-1]
                    if filename.endswith(".m2v"):
                        return filename
        return None

    @staticmethod
    def find_file(start_path, filename):
        if os.path.exists(os.path.join(start_path, filename)):
            return os.path.join(start_path, filename)

        for root, dirs, files in os.walk(start_path):
            if filename in files:
                eslog.debug("Found m2v file in path - {}".format(os.path.join(root, filename)))
                return os.path.join(root, filename)

        return None

    @staticmethod
    def get_resolution(video_path):
        cap = cv2.VideoCapture(video_path)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()
        return width, height

    # Main entry of the module
    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        # copy input.ini file templates
        hypseusConfigSource = "/usr/share/hypseus-singe/hypinput_gamepad.ini"

        if not os.path.isdir(batoceraFiles.hypseusDatadir):
            os.mkdir(batoceraFiles.hypseusDatadir)
        if not os.path.exists(batoceraFiles.hypseusConfig) or not filecmp.cmp(hypseusConfigSource, batoceraFiles.hypseusConfig):
            shutil.copyfile(hypseusConfigSource, batoceraFiles.hypseusConfig)

        # create a custom ini
        if not os.path.exists(batoceraFiles.hypseusDatadir + "/custom.ini"):
            shutil.copyfile(batoceraFiles.hypseusConfig, batoceraFiles.hypseusDatadir + "/custom.ini")

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
                            shutil.copy2(source_item, destination_item)
                    elif os.path.isdir(source_item):
                        copy_resources(source_item, destination_item)

        directories = [
            {"source": "/usr/share/hypseus-singe/pics", "destination": batoceraFiles.hypseusDatadir + "/pics"},
            {"source": "/usr/share/hypseus-singe/sound", "destination": batoceraFiles.hypseusDatadir + "/sound"},
            {"source": "/usr/share/hypseus-singe/fonts", "destination": batoceraFiles.hypseusDatadir + "/fonts"},
            {"source": "/usr/share/hypseus-singe/bezels", "destination": batoceraFiles.hypseusDatadir + "/bezels"}
        ]

        # Copy/update directories
        for directory in directories:
            copy_resources(directory["source"], directory["destination"])
               
        # extension used .daphne and the file to start the game is in the folder .daphne with the extension .txt
        romName = os.path.splitext(os.path.basename(rom))[0]
        frameFile = rom + "/" + romName + ".txt"
        commandsFile = rom + "/" + romName + ".commands"
        singeFile = rom + "/" + romName + ".singe"
        
        bezelFile = romName + ".png"
        bezelPath = batoceraFiles.hypseusDatadir + "/bezels/" + bezelFile
        sindenBezelPath = batoceraFiles.hypseusDatadir + "/bezels/sinden/" + bezelFile

        # get the first video file from frameFile to determine the resolution
        m2v_filename = self.find_m2v_from_txt(frameFile)

        if m2v_filename:
            eslog.debug("First .m2v file found: {}".format(m2v_filename))
        else:
            eslog.debug("No .m2v files found in the text file.")

        # now get the resolution from the m2v file
        video_path = rom + "/" + m2v_filename
        # check the path exists
        if not os.path.exists(video_path):
            eslog.debug("Could not find m2v file in path - {}".format(video_path))
            video_path = self.find_file(rom, m2v_filename)

        eslog.debug("Full m2v path is: {}".format(video_path))

        if video_path != None:
            video_resolution = self.get_resolution(video_path)
            eslog.debug("Resolution: {}".format(video_resolution))

        if system.name == "singe":
            commandArray = [batoceraFiles.batoceraBins[system.config['emulator']],
                            "singe", "vldp", "-retropath", "-framefile", frameFile, "-script", singeFile,
                            "-fullscreen", "-gamepad", "-datadir", batoceraFiles.hypseusDatadir,
                            "-romdir", batoceraFiles.singeRomdir, "-homedir", batoceraFiles.hypseusDatadir]
        else:
            commandArray = [batoceraFiles.batoceraBins[system.config['emulator']],
                            romName, "vldp", "-framefile", frameFile, "-fullscreen",
                            "-fastboot", "-gamepad", "-datadir", batoceraFiles.hypseusDatadir, 
                            "-romdir", batoceraFiles.daphneRomdir, "-homedir", batoceraFiles.hypseusDatadir]

        # controller config file
        if system.isOptSet('hypseus_joy')  and system.getOptBoolean('hypseus_joy'):
            commandArray.extend(['-keymapfile', 'custom.ini'])
        else:
            commandArray.extend(["-keymapfile", batoceraFiles.hypseusConfigfile])

        # Default -fullscreen behaviour respects game aspect ratio
        bezelRequired = False
        # stretch
        if system.isOptSet('hypseus_ratio') and system.config['hypseus_ratio'] == "stretch":
            commandArray.extend(["-x", str(gameResolution["width"]), "-y", str(gameResolution["height"])])
            bezelRequired = False
        # 4:3
        elif system.isOptSet('hypseus_ratio') and system.config['hypseus_ratio'] == "force_ratio":
            commandArray.extend(["-x", str(gameResolution["width"]), "-y", str(gameResolution["height"])])
            commandArray.extend(["-force_aspect_ratio"])
            bezelRequired = True
        # original
        else:
            if video_resolution[0] != "0":
                scaling_factor = gameResolution["height"] / video_resolution[1]
                screen_width = gameResolution["width"]
                new_width = video_resolution[0] * scaling_factor
                commandArray.extend(["-x", str(new_width), "-y", str(gameResolution["height"])])
                # check if 4:3 for bezels
                if abs(new_width / gameResolution["height"] - 4/3) < 0.01:
                    bezelRequired = True
                else:
                    bezelRequired = False
            else:
                eslog.debug("Video resolution not found - using stretch")
                commandArray.extend(["-x", str(gameResolution["width"]), "-y", str(gameResolution["height"])])

        # Backend - Default OpenGL
        if system.isOptSet("hypseus_api") and system.config["hypseus_api"] == 'Vulkan':
            commandArray.append("-vulkan")
        else:
            commandArray.append("-opengl")

        # Enable Bilinear Filtering
        if system.isOptSet('hypseus_filter') and system.getOptBoolean("hypseus_filter"):
            commandArray.append("-linear_scale")

        #The following options should only be set when system is singe.
        #-blend_sprites, -nocrosshair, -sinden or -manymouse
        if system.name == "singe":
            # Blend Sprites (Singe)
            if system.isOptSet('singe_sprites') and system.getOptBoolean("singe_sprites"):
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
                    if system.isOptSet('singe_abs') and system.getOptBoolean("singe_abs"):
                        commandArray.extend(["-manymouse"]) # this is causing issues on some "non-gun" games

        # bezels
        if bezelRequired:
            bordersSize = controllersConfig.gunsBordersSizeName(guns, system.config)
            if bordersSize is not None:
                if not os.path.exists(sindenBezelPath):
                    commandArray.extend(["-bezel", "Daphne.png"])
                else:
                    commandArray.extend(["-bezel", "sinden/" + bezelFile])
            else:
                if not os.path.exists(bezelPath):
                    commandArray.extend(["-bezel", "Daphne.png"])
                else:
                    commandArray.extend(["-bezel", bezelFile])

        # Invert HAT Axis
        if system.isOptSet('hypseus_axis') and system.getOptBoolean("hypseus_axis"):
            commandArray.append("-tiphat")

        # Game rotation options for vertical screens, default is 0.
        if system.isOptSet('hypseus_rotate') and system.config['hypseus_rotate'] == "90":
            commandArray.extend(["-rotate", "90"])
        elif system.isOptSet('hypseus_rotate') and system.config['hypseus_rotate'] == "270":
            commandArray.extend(["-rotate", "270"])

        # Singe joystick sensitivity, default is 5.
        if system.name == "singe" and system.isOptSet('singe_joystick_range') and system.config['singe_joystick_range'] == "10":
            commandArray.extend(["-js_range", "10"])
        elif system.name == "singe" and system.isOptSet('singe_joystick_range') and system.config['singe_joystick_range'] == "15":
            commandArray.extend(["-js_range", "15"])
        elif system.name == "singe" and system.isOptSet('singe_joystick_range') and system.config['singe_joystick_range'] == "20":
            commandArray.extend(["-js_range", "20"])

        # Scanlines
        if system.isOptSet('hypseus_scanlines') and system.getOptBoolean("hypseus_scanlines"):
            commandArray.append("-scanlines")

        # Hide crosshair in supported games (e.g. ActionMax, ALG)
        # needCrosshair
        if len(guns) > 0 and (not system.isOptSet('singe_crosshair') or ((system.isOptSet('singe_crosshair') and not system.config["singe_crosshair"]))):
            commandArray.append("-nocrosshair")

        # Enable SDL_TEXTUREACCESS_STREAMING, can aid SBC's with SDL2 => 2.0.16
        if system.isOptSet('hypseus_texturestream') and system.getOptBoolean("hypseus_texturestream"):
            commandArray.append("-texturestream")

        # The folder may have a file with the game name and .commands with extra arguments to run the game.
        if os.path.isfile(commandsFile):
            commandArray.extend(open(commandsFile,'r').read().split())

        # We now use SDL controller config
        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers),
                'SDL_JOYSTICK_HIDAPI': '0',
                'MANYMOUSE_NO_XINPUT2': 'x' # disable xorg mouse => forces evdev mouse
            }
        )

    def getInGameRatio(self, config, gameResolution, rom):
        if "hypseus_ratio" in config:
            if config['hypseus_ratio'] == "stretch":
                return 16/9
            if config['hypseus_ratio'] == "force_ratio":
                return 4/3
        else:
            return 4/3
