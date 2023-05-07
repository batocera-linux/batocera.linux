#!/usr/bin/env python

from generators.Generator import Generator
import batoceraFiles
import Command
import shutil
import os
from os import path
from os import environ
import configparser
import ruamel.yaml as yaml
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

        with open(batoceraFiles.rpcs3CurrentConfig, "w") as configfile:
            rpcsCurrentSettings.write(configfile)

        if not os.path.exists(os.path.dirname(batoceraFiles.rpcs3config)):
            os.makedirs(os.path.dirname(batoceraFiles.rpcs3config))

        # Generate a default config if it doesn't exist otherwise just open the existing
        rpcs3ymlconfig = {}
        if os.path.isfile(batoceraFiles.rpcs3config):
            with open(batoceraFiles.rpcs3config, "r") as stream:
                rpcs3ymlconfig = yaml.safe_load(stream)

        if rpcs3ymlconfig is None: # in case the file is empty
            rpcs3ymlconfig = {}

        # Add Nodes if not in the file
        if "Core" not in rpcs3ymlconfig:
            rpcs3ymlconfig["Core"] = {}
        if "VFS" not in rpcs3ymlconfig:
            rpcs3ymlconfig["VFS"] = {}
        if "Video" not in rpcs3ymlconfig:
            rpcs3ymlconfig["Video"] = {}
        if "Audio" not in rpcs3ymlconfig:
            rpcs3ymlconfig["Audio"] = {}
        if "Input/Output" not in rpcs3ymlconfig:
            rpcs3ymlconfig["Input/Output"] = {}
        if "System" not in rpcs3ymlconfig:
            rpcs3ymlconfig["System"] = {}
        if "Net" not in rpcs3ymlconfig:
            rpcs3ymlconfig["Net"] = {}
        if "Savestate" not in rpcs3ymlconfig:
            rpcs3ymlconfig["Savestate"] = {}
        if "Miscellaneous" not in rpcs3ymlconfig:
            rpcs3ymlconfig["Miscellaneous"] = {}
        if "Log" not in rpcs3ymlconfig:
            rpcs3ymlconfig["Log"] = {}

        # -= [Core] =-
        # Set the PPU Decoder based on config
        if system.isOptSet("rpcs3_ppudecoder"):
            rpcs3ymlconfig["Core"]["PPU Decoder"] = system.config["rpcs3_ppudecoder"]
        else:
            rpcs3ymlconfig["Core"]["PPU Decoder"] = "Recompiler (LLVM)"
        # Set the SPU Decoder based on config
        if system.isOptSet("rpcs3_spudecoder"):
            rpcs3ymlconfig["Core"]["SPU Decoder"] = system.config["rpcs3_spudecoder"]
        else:
            rpcs3ymlconfig["Core"]["SPU Decoder"] = "Recompiler (LLVM)"
        # Set the SPU XFloat Accuracy based on config
        rpcs3ymlconfig["Core"]["Accurate xfloat"] = False
        rpcs3ymlconfig["Core"]["Approximate xfloat"] = True
        # This is not an oversight. Relaxed xfloat is always set to "true" by the RPCS3 config menu.
        rpcs3ymlconfig["Core"]["Relaxed xfloat"] = True
        if system.isOptSet("rpcs3_spuxfloataccuracy"):
            if system.config["rpcs3_spuxfloataccuracy"] == "accurate":
                rpcs3ymlconfig["Core"]["Accurate xfloat"] = True
                rpcs3ymlconfig["Core"]["Approximate xfloat"] = False
            elif system.config["rpcs3_spuxfloataccuracy"] == "relaxed":
                rpcs3ymlconfig["Core"]["Accurate xfloat"] = False
                rpcs3ymlconfig["Core"]["Approximate xfloat"] = False
        # Set the Default Core Values we need
        rpcs3ymlconfig["Core"]["SPU Cache"] = False # When SPU Cache is True, game performance decreases signficantly. Force it to off.
        # Preferred SPU Threads
        if system.isOptSet("rpcs3_sputhreads"):
            rpcs3ymlconfig["Core"]["Preferred SPU Threads"] = system.config["rpcs3_sputhreads"]
        else:
            rpcs3ymlconfig["Core"]["Preferred SPU Threads"] = 0

        # -= [Video] =-
        # gfx backend - default to Vulkan
        if system.isOptSet("rpcs3_gfxbackend"):
            rpcs3ymlconfig["Video"]["Renderer"] = system.config["rpcs3_gfxbackend"]
        else:
            rpcs3ymlconfig["Video"]["Renderer"] = "Vulkan"
        # System aspect ratio (the setting in the PS3 system itself, not the displayed ratio) a.k.a. TV mode.
        if system.isOptSet("rpcs3_ratio"):
            rpcs3ymlconfig["Video"]["Aspect ratio"] = system.config["rpcs3_ratio"]
        else:
            # If not set, see if the screen ratio is closer to 4:3 or 16:9 and pick that.
            rpcs3ymlconfig["Video"]["Aspect ratio"] = ":".join(map(str, Rpcs3Generator.getClosestRatio(gameResolution)))
        # Shader compilation
        if system.isOptSet("rpcs3_shadermode"):
            rpcs3ymlconfig["Video"]["Shader Mode"] = system.config["rpcs3_shadermode"]
        else:
            rpcs3ymlconfig["Video"]["Shader Mode"] = "Async Shader Recompiler"
        # Vsync
        if system.isOptSet("rpcs3_vsync"):
            rpcs3ymlconfig["Video"]["VSync"] = system.config["rpcs3_vsync"]
        else:
            rpcs3ymlconfig["Video"]["VSync"] = False
        # Stretch to display area
        if system.isOptSet("rpcs3_stretchdisplay"):
            rpcs3ymlconfig["Video"]["Stretch To Display Area"] = system.config["rpcs3_stretchdisplay"]
        else:
            rpcs3ymlconfig["Video"]["Stretch To Display Area"] = False
        # Frame Limit
        if system.isOptSet("rpcs3_framelimit"):
            rpcs3ymlconfig["Video"]["Frame limit"] = system.config["rpcs3_framelimit"]
        else:
            rpcs3ymlconfig["Video"]["Frame limit"] = "Auto"
        # Write Color Buffers
        if system.isOptSet("rpcs3_colorbuffers"):
            rpcs3ymlconfig["Video"]["Write Color Buffers"] = system.config["rpcs3_colorbuffers"]
        else:
            rpcs3ymlconfig["Video"]["Write Color Buffers"] = False
        # Disable Vertex Cache
        if system.isOptSet("rpcs3_vertexcache"):
            rpcs3ymlconfig["Video"]["Disable Vertex Cache"] = system.config["rpcs3_vertexcache"]
        else:
            rpcs3ymlconfig["Video"]["Disable Vertex Cache"] = False
        # Anisotropic Filtering
        if system.isOptSet("rpcs3_anisotropic"):
            rpcs3ymlconfig["Video"]["Anisotropic Filter Override"] = system.config["rpcs3_anisotropic"]
        else:
            rpcs3ymlconfig["Video"]["Anisotropic Filter Override"] = 0
        # MSAA
        if system.isOptSet("rpcs3_aa"):
            rpcs3ymlconfig["Video"]["MSAA"] = system.config["rpcs3_aa"]
        else:
            rpcs3ymlconfig["Video"]["MSAA"] = "Auto"
        # ZCULL
        if system.isOptSet("rpcs3_zcull") and system.config["rpcs3_zcull"] == "Approximate":
            rpcs3ymlconfig["Video"]["Accurate ZCULL stats"] = False
            rpcs3ymlconfig["Video"]["Relaxed ZCULL Sync"] = False
        elif system.isOptSet("rpcs3_zcull") and system.config["rpcs3_zcull"] == "Relaxed":
            rpcs3ymlconfig["Video"]["Accurate ZCULL stats"] = False
            rpcs3ymlconfig["Video"]["Relaxed ZCULL Sync"] = True
        else:
            rpcs3ymlconfig["Video"]["Accurate ZCULL stats"] = True
            rpcs3ymlconfig["Video"]["Relaxed ZCULL Sync"] = False
        # Shader Precision
        if system.isOptSet("rpcs3_shader"):
            rpcs3ymlconfig["Video"]["Shader Precision"] = system.config["rpcs3_shader"]
        else:
            rpcs3ymlconfig["Video"]["Shader Precision"] = "High"
        # Resolution
        if system.isOptSet("rpcs3_resolution"):
            rpcs3ymlconfig["Video"]["Resolution"] = system.config["rpcs3_resolution"]
        else:
            rpcs3ymlconfig["Video"]["Resolution"] = "1280x720"
        # Output Scaling
        if system.isOptSet("rpcs3_scaling"):
            rpcs3ymlconfig["Video"]["Output Scaling Mode"] = system.config["rpcs3_scaling"]
        else:
            rpcs3ymlconfig["Video"]["Output Scaling Mode"] = "Bilinear"
        # Number of Shader Compilers
        if system.isOptSet("rpcs3_num_compilers"):
            rpcs3ymlconfig["Video"]["Shader Compiler Threads"] = system.config["rpcs3_num_compilers"]
        else:
            rpcs3ymlconfig["Video"]["Shader Compiler Threads"] = 0
        # Multithreaded RSX
        if system.isOptSet("rpcs3_rsx"):
            rpcs3ymlconfig["Video"]["Multithreaded RSX"] = system.config["rpcs3_rsx"]
        else:
            rpcs3ymlconfig["Video"]["Multithreaded RSX"] = False
        
        # -= [Audio] =-
        # defaults
        rpcs3ymlconfig["Audio"]["Renderer"] = "Cubeb"
        rpcs3ymlconfig["Audio"]["Master Volume"] = 100
        # audio format
        if system.isOptSet("rpcs3_audio_format"):
            rpcs3ymlconfig["Audio"]["Audio Format"] = system.config["rpcs3_audio_format"]
        else:
            rpcs3ymlconfig["Audio"]["Audio Format"] = "Stereo"
        # audio buffering
        if system.isOptSet("rpcs3_audiobuffer"):
            rpcs3ymlconfig["Audio"]["Enable Buffering"] = system.config["rpcs3_audiobuffer"]
        else:
            rpcs3ymlconfig["Audio"]["Enable Buffering"] = True
        rpcs3ymlconfig["Audio"]["Desired Audio Buffer Duration"] = 100
        # time stretching
        if system.isOptSet("rpcs3_timestretch") and system.config["rpcs3_timestretch"] == "True":
            rpcs3ymlconfig["Audio"]["Enable Time Stretching"] = True
            rpcs3ymlconfig["Audio"]["Enable Buffering"] = True
        else:
            rpcs3ymlconfig["Audio"]["Enable Time Stretching"] = False
        rpcs3ymlconfig["Audio"]["Time Stretching Threshold"] = 75

        # -= [Input/Output] =-
        # gun stuff
        if system.isOptSet("use_guns") and system.getOptBoolean("use_guns") and len(guns) > 0:
            rpcs3ymlconfig["Input/Output"]["Move"] = "Gun"
            rpcs3ymlconfig["Input/Output"]["Camera"] = "Fake"
            rpcs3ymlconfig["Input/Output"]["Camera type"] = "PS Eye"

        # -= [Miscellaneous] =-
        rpcs3ymlconfig["Miscellaneous"]["Exit RPCS3 when process finishes"] = True
        rpcs3ymlconfig["Miscellaneous"]["Start games in fullscreen mode"] = True
        rpcs3ymlconfig["Miscellaneous"]["Show shader compilation hint"] = False
        rpcs3ymlconfig["Miscellaneous"]["Prevent display sleep while running games"] = True
        rpcs3ymlconfig["Miscellaneous"]["Show trophy popups"] = False

        with open(batoceraFiles.rpcs3config, "w") as file:
            yaml.dump(rpcs3ymlconfig, file, default_flow_style=False)
                
        # determine the rom name
        if rom.endswith(".psn"):
            with open(rom) as fp:
                for line in fp:
                    if len(line) >= 9:
                        romName = "/userdata/system/configs/rpcs3/dev_hdd0/game/" + line.strip().upper() + "/USRDIR/EBOOT.BIN"
        else:
            romBasename = path.basename(rom)
            romName = rom + "/PS3_GAME/USRDIR/EBOOT.BIN"
        
        commandArray = [batoceraFiles.batoceraBins[system.config["emulator"]], romName]

        if not (system.isOptSet("rpcs3_gui") and system.getOptBoolean("rpcs3_gui")):
            commandArray.append("--no-gui")

        # firmware not installed and available : instead of starting the game, install it
        if Rpcs3Generator.getFirmwareVersion() is None:
          if os.path.exists("/userdata/bios/PS3UPDAT.PUP"):
            commandArray = [batoceraFiles.batoceraBins[system.config["emulator"]], "--installfw", "/userdata/bios/PS3UPDAT.PUP"]

        return Command.Command(array=commandArray, env={"XDG_CONFIG_HOME":batoceraFiles.CONF, "XDG_CACHE_HOME":batoceraFiles.CACHE, "QT_QPA_PLATFORM":"xcb"})

    def getClosestRatio(gameResolution):
        screenRatio = gameResolution["width"] / gameResolution["height"]
        if screenRatio < 1.6:
            return (4,3)
        else:
            return (16,9)

    def getInGameRatio(self, config, gameResolution, rom):
        return 16/9

    def getFirmwareVersion():
        try:
            with open("/userdata/system/configs/rpcs3/dev_flash/vsh/etc/version.txt", "r") as stream:
                lines = stream.readlines()
            for line in lines:
                matches = re.match("^release:(.*):", line)
                if matches:
                    return matches[1]
        except:
            return None
        return None
