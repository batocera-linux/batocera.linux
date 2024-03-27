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

class DaphneGenerator(Generator):

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
                            shutil.copy2(source_item, destination_item)
                    elif os.path.isdir(source_item):
                        copy_resources(source_item, destination_item)

        directories = [
            {"source": "/usr/share/daphne/pics", "destination": batoceraFiles.daphneDatadir + "/pics"},
            {"source": "/usr/share/daphne/sound", "destination": batoceraFiles.daphneDatadir + "/sound"},
            {"source": "/usr/share/daphne/fonts", "destination": batoceraFiles.daphneDatadir + "/fonts"},
            {"source": "/usr/share/daphne/bezels", "destination": batoceraFiles.daphneDatadir + "/bezels"}
        ]

        # Copy/update directories
        for directory in directories:
            copy_resources(directory["source"], directory["destination"])

        # create symbolic link for singe
        if not os.path.exists(batoceraFiles.daphneDatadir + "/singe"):
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
        bezelFile = romName + ".png"
        bezelPath = "/userdata/system/configs/daphne/bezels/" + bezelFile
        sindenBezelPath = "/userdata/system/configs/daphne/bezels/sinden/" + bezelFile

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
        bezelRequired = False
        # stretch
        if system.isOptSet('daphne_ratio') and system.config['daphne_ratio'] == "stretch":
            commandArray.extend(["-x", str(gameResolution["width"]), "-y", str(gameResolution["height"])])
            bezelRequired = False
        # 4:3
        elif system.isOptSet('daphne_ratio') and system.config['daphne_ratio'] == "force_ratio":
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
        # needCrosshair
        if len(guns) > 0 and (not system.isOptSet('singe_crosshair') or ((system.isOptSet('singe_crosshair') and not system.config["singe_crosshair"]))):
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
