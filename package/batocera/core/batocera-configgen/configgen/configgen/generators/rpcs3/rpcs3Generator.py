#!/usr/bin/env python

from generators.Generator import Generator
import batoceraFiles
import Command
import shutil
import os
from os import path
from os import environ
import configparser
import yaml
import json
import re
from . import rpcs3Controllers

class Rpcs3Generator(Generator):

    def generate(self, system, rom, playersControllers, guns, gameResolution):

        rpcs3Controllers.generateControllerConfig(system, playersControllers, rom)

        # Taking care of the CurrentSettings.ini file
        if not os.path.exists(os.path.dirname(batoceraFiles.rpcs3CurrentConfig)):
            os.makedirs(os.path.dirname(batoceraFiles.rpcs3CurrentConfig))

        # Generates CurrentSettings.ini with values to disable prompts on first run

        rpcsCurrentSettings = configparser.ConfigParser(interpolation=None)
        # To prevent ConfigParser from converting to lower case
        rpcsCurrentSettings.optionxform = str
        if os.path.exists(batoceraFiles.rpcs3CurrentConfig):
            rpcsCurrentSettings.read(batoceraFiles.rpcs3CurrentConfig)

        # Sets Gui Settings to close completely and disables some popups
        if not rpcsCurrentSettings.has_section("main_window"):
            rpcsCurrentSettings.add_section("main_window")

        rpcsCurrentSettings.set("main_window", "confirmationBoxExitGame", "false")
        rpcsCurrentSettings.set("main_window", "infoBoxEnabledInstallPUP","false")
        rpcsCurrentSettings.set("main_window", "infoBoxEnabledWelcome","false")

        with open(batoceraFiles.rpcs3CurrentConfig, 'w') as configfile:
            rpcsCurrentSettings.write(configfile)

        if not os.path.exists(os.path.dirname(batoceraFiles.rpcs3config)):
            os.makedirs(os.path.dirname(batoceraFiles.rpcs3config))

        # Generate a default config if it doesn't exist otherwise just open the existing
        rpcs3ymlconfig = {}
        if os.path.isfile(batoceraFiles.rpcs3config):
            with open(batoceraFiles.rpcs3config, 'r') as stream:
                rpcs3ymlconfig = yaml.safe_load(stream)

        if rpcs3ymlconfig is None: # in case the file is empty
            rpcs3ymlconfig = {}

        # Add Node Core
        if "Core" not in rpcs3ymlconfig:
            rpcs3ymlconfig["Core"] = {}
        # Add Node Video
        if "Video" not in rpcs3ymlconfig:
            rpcs3ymlconfig["Video"] = {}
        # Add Node Audio
        if "Audio" not in rpcs3ymlconfig:
            rpcs3ymlconfig["Audio"] = {}
        # Add Node Miscellaneous
        if "Miscellaneous" not in rpcs3ymlconfig:
            rpcs3ymlconfig["Miscellaneous"] = {}
        if "Input/Output" not in rpcs3ymlconfig:
            rpcs3ymlconfig["Input/Output"] = {}

        # [Core]
        # Set the PPU Decoder based on config
        if system.isOptSet("ppudecoder"):
            rpcs3ymlconfig["Core"]['PPU Decoder'] = system.config["ppudecoder"]
        else:
            rpcs3ymlconfig["Core"]['PPU Decoder'] = 'Recompiler (LLVM)'
        # Set the SPU Decoder based on config
        if system.isOptSet("spudecoder"):
            rpcs3ymlconfig["Core"]['SPU Decoder'] = system.config["spudecoder"]
        else:
            rpcs3ymlconfig["Core"]['SPU Decoder'] = 'Recompiler (LLVM)'

        # Set the SPU XFloat Accuracy based on config
        rpcs3ymlconfig["Core"]['Accurate xfloat'] = "false"
        rpcs3ymlconfig["Core"]['Approximate xfloat'] = "true"
        # This is not an oversight. Relaxed xfloat is always set to "true" by the RPCS3 config menu.
        rpcs3ymlconfig["Core"]['Relaxed xfloat'] = "true"
        if system.isOptSet("spuxfloataccuracy"):
            if system.config["spuxfloataccuracy"] == "accurate":
                rpcs3ymlconfig["Core"]['Accurate xfloat'] = "true"
                rpcs3ymlconfig["Core"]['Approximate xfloat'] = "false"
            # This is what is set by default.
            # elif system.config["spuxfloataccuracy"] == "approximate":
            #     rpcs3ymlconfig["Core"]['Accurate xfloat'] = "false"
            #     rpcs3ymlconfig["Core"]['Approximate xfloat'] = "true"
            elif system.config["spuxfloataccuracy"] == "relaxed":
                rpcs3ymlconfig["Core"]['Accurate xfloat'] = "false"
                rpcs3ymlconfig["Core"]['Approximate xfloat'] = "false"

        # Set the Default Core Values we need
        rpcs3ymlconfig["Core"]['Lower SPU thread priority'] = False
        rpcs3ymlconfig["Core"]['SPU Cache'] = False # When SPU Cache is True, game performance decreases signficantly. Force it to off.
        rpcs3ymlconfig["Core"]['PPU LLVM Accurate Vector NaN values'] = True
        # Preferred SPU Threads
        if system.isOptSet("sputhreads"):
            rpcs3ymlconfig["Core"]['Preferred SPU Threads'] = system.config["sputhreads"]
        else:
            rpcs3ymlconfig["Core"]['Preferred SPU Threads'] = 0

        # [Video]
        # gfx backend
        if system.isOptSet("gfxbackend"):
            rpcs3ymlconfig["Video"]['Renderer'] = system.config["gfxbackend"]
        else:
            rpcs3ymlconfig["Video"]['Renderer'] = 'OpenGL' # Vulkan
        # System aspect ratio (the setting in the PS3 system itself, not the displayed ratio) a.k.a. TV mode.
        if system.isOptSet("tv_mode"):
            if system.config['tv_mode'] == '4/3':
                rpcs3ymlconfig["Video"]['Aspect ratio'] = '4:3'
            elif system.config['tv_mode'] == '16/9':
                rpcs3ymlconfig["Video"]['Aspect ratio'] = '16:9'
        else:
            # If not set, see if the screen ratio is closer to 4:3 or 16:9 and pick that.
            rpcs3ymlconfig["Video"]['Aspect ratio'] = Rpcs3Generator.getClosestRatio(gameResolution)
        # Shader compilation
        if system.isOptSet("shadermode"):
            rpcs3ymlconfig["Video"]['Shader Mode'] = system.config['shadermode']
        else:
            # RPCS3's default "Async Shader Recompiler" has visual glitches, however it's the only setting which doesn't cause the screen to freeze whenever new graphics are on screen. If RPCS3 ever fixes the "Async with Shader Interpreter" option, it would be the preferred option for this setting.
            rpcs3ymlconfig["Video"]['Shader Mode'] = str("Async Shader Recompiler")
        # Vsync defaults to off because ??? it's faster? Not sure why, but not changing it.
        if system.isOptSet("vsync") and system.getOptBoolean("vsync"):
            rpcs3ymlconfig["Video"]['VSync'] = True
        else:
            rpcs3ymlconfig["Video"]['VSync'] = False
        # Stretch to display area
        if system.isOptSet("stretchtodisplayarea") and system.getOptBoolean("stretchtodisplayarea"):
            rpcs3ymlconfig["Video"]['Stretch To Display Area'] = True
        else:
            rpcs3ymlconfig["Video"]['Stretch To Display Area'] = False
        # Frame Limit
        if system.isOptSet("framelimit"):
            rpcs3ymlconfig["Video"]['Frame limit'] = system.config['framelimit']
        else:
            rpcs3ymlconfig["Video"]['Frame limit'] = 60
        # Write Depth Buffer
        if system.isOptSet("depthbuffer"):
            rpcs3ymlconfig["Video"]['Write Depth Buffer'] = system.config['depthbuffer']
        else:
            rpcs3ymlconfig["Video"]['Write Depth Buffer'] = False
        # Write Color Buffers
        if system.isOptSet("colorbuffers"):
            rpcs3ymlconfig["Video"]['Write Color Buffers'] = system.config['colorbuffers']
        else:
            rpcs3ymlconfig["Video"]['Write Color Buffers'] = False
        # Disable Vertex Cache
        if system.isOptSet("vertexcache"):
            rpcs3ymlconfig["Video"]['Disable Vertex Cache'] = system.config['vertexcache']
        else:
            rpcs3ymlconfig["Video"]['Disable Vertex Cache'] = False

        # [Audio]
        rpcs3ymlconfig["Audio"]['Renderer'] = 'Cubeb' # ALSA does not support buffering so we have sound cuts ex: Rayman Origin
        rpcs3ymlconfig["Audio"]['Master Volume'] = 100
        rpcs3ymlconfig["Audio"]['Audio Channels'] = 'Downmix to Stereo'

        # [Miscellaneous]
        rpcs3ymlconfig["Miscellaneous"]['Exit RPCS3 when process finishes'] = True
        rpcs3ymlconfig["Miscellaneous"]['Start games in fullscreen mode'] = True

        # input/output
        if system.isOptSet('use_guns') and system.getOptBoolean('use_guns') and len(guns) > 0:
            rpcs3ymlconfig["Input/Output"]["Move"] = "Gun"
            rpcs3ymlconfig["Input/Output"]["Camera"] = "Fake"
            rpcs3ymlconfig["Input/Output"]["Camera type"] = "PS Eye"

        with open(batoceraFiles.rpcs3config, 'w') as file:
            documents = yaml.safe_dump(rpcs3ymlconfig, file, default_flow_style=False)
        if rom.endswith(".psn"):
            with open(rom) as fp:
                for line in fp:
                    if len(line) >= 9:
                        romName = '/userdata/system/configs/rpcs3/dev_hdd0/game/' + line.strip().upper() + "/USRDIR/EBOOT.BIN"
        else:
            romBasename = path.basename(rom)
            romName = rom + '/PS3_GAME/USRDIR/EBOOT.BIN'
        commandArray = [batoceraFiles.batoceraBins[system.config['emulator']], romName]

        if not (system.isOptSet("gui") and system.getOptBoolean("gui")):
            commandArray.append("--no-gui")

        # firmware not installed and available : instead of starting the game, install it
        if Rpcs3Generator.getFirmwareVersion() is None:
          if os.path.exists("/userdata/bios/PS3UPDAT.PUP"):
            commandArray = [batoceraFiles.batoceraBins[system.config['emulator']], "--installfw", "/userdata/bios/PS3UPDAT.PUP"]

        return Command.Command(array=commandArray, env={"XDG_CONFIG_HOME":batoceraFiles.CONF, "XDG_CACHE_HOME":batoceraFiles.CACHE, "QT_QPA_PLATFORM":"xcb"})

    def getClosestRatio(gameResolution):
        # Works out the closest screen aspect ratio between the two rpcs3 options - 4:3 and 16:9.
        # 4:3 = 1.33, 16:10 (Steam Deck) = 1.6, 16:9 = 1.77.
        # We assume if the ratio is narrower than 16:10 we probably want 4:3, otherwise 16:10 or wider will return 16:9.
        screenRatio = gameResolution['width'] / gameResolution['height']
        if screenRatio < 1.6:
            return '4:3'
        else:
            return '16:9'

    def getInGameRatio(self, config, gameResolution, rom):
        # If stretchy-boy mode has been set, just assume the display resolution is the aspect ratio.
        #if config.isOptSet("stretchtodisplayarea") and config.getOptBoolean("stretchtodisplayarea"):
            #return gameResolution["width"] / gameResolution["height"]

        # Check if the aspect ratio key exists.
        #if config.isOptSet("tv_mode"):
            #return config['tv_mode']
        #else:
            return 16/9

    def getFirmwareVersion():
        try:
            with open("/userdata/system/configs/rpcs3/dev_flash/vsh/etc/version.txt", 'r') as stream:
                lines = stream.readlines()
            for line in lines:
                matches = re.match("^release:(.*):", line)
                if matches:
                    return matches[1]
        except:
            return None
        return None
