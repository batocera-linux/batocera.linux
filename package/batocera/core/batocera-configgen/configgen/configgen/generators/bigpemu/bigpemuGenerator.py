#!/usr/bin/env python3

from generators.Generator import Generator
import Command
import os
import sys
import json
import utils.videoMode as videoMode
import controllersConfig

bigPemuConfig = "/userdata/system/.bigpemu_userdata/BigPEmuConfig.bigpcfg"

class BigPEmuGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        directory = os.path.dirname(bigPemuConfig)
        # Create the directory if it doesn't exist
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        # Create the config file if it doesn't exist
        if not os.path.exists(bigPemuConfig):
            with open(bigPemuConfig, "w") as file:
                json.dump({}, file)
        
        # Load or initialize the configuration
        with open(bigPemuConfig, "r") as file:
            try:
                config = json.load(file)
            except json.decoder.JSONDecodeError:
                config = {}
        
        # Ensure the necessary structure in the config
        if "BigPEmuConfig" not in config:
            config["BigPEmuConfig"] = {}
        if "Video" not in config["BigPEmuConfig"]:
            config["BigPEmuConfig"]["Video"] = {}
        
        # Adjust basic settings
        config["BigPEmuConfig"]["Video"]["DisplayMode"] = 2
        config["BigPEmuConfig"]["Video"]["ScreenScaling"] = 5
        config["BigPEmuConfig"]["Video"]["DisplayWidth"] = gameResolution["width"]
        config["BigPEmuConfig"]["Video"]["DisplayHeight"] = gameResolution["height"]
        config["BigPEmuConfig"]["Video"]["DisplayFrequency"] = int(videoMode.getRefreshRate())
        
        # User selections
        if system.isOptSet("bigpemu_vsync"):
            config["BigPEmuConfig"]["Video"]["VSync"] = system.config["bigpemu_vsync"]
        else:
            config["BigPEmuConfig"]["Video"]["VSync"] = 1
        if system.isOptSet("bigpemu_ratio"):
            config["BigPEmuConfig"]["Video"]["ScreenAspect"] = system.config["bigpemu_ratio"]
        else:
            config["BigPEmuConfig"]["Video"]["ScreenAspect"] = 2
        
        with open(bigPemuConfig, "w") as file:
            json.dump(config, file, indent=4)

        # Run the emulator
        commandArray = ["/usr/bigpemu/bigpemu", rom]

        environment = {
            "SDL_GAMECONTROLLERCONFIG": controllersConfig.generateSdlGameControllerConfig(playersControllers)
        }
        
        return Command.Command(array=commandArray, env=environment)

    def getInGameRatio(self, config, gameResolution, rom):
        if "bigpemu_ratio" in config:
            if config['bigpemu_ratio'] == "8":
                return 16/9
            else:
                return 4/3
        else:
            return 4/3
