#!/usr/bin/env python

import Command
import batoceraFiles
from generators.Generator import Generator
import controllersConfig
import os
from os import path
import yaml
from distutils.dir_util import copy_tree

vitaConfig = batoceraFiles.CONF + '/vita3k'
vitaSaves = batoceraFiles.SAVES + '/psvita'
vitaConfigFile = vitaConfig + '/config.yml'

class Vita3kGenerator(Generator):

    def generate(self, system, rom, playersControllers, guns, gameResolution):

        # Create config folder
        if not path.isdir(vitaConfig):
            os.mkdir(vitaConfig)
            # copy /usr/bin/vita3k contents here
            copy_tree("/usr/bin/vita3k", vitaConfig)

        # Create save folder
        if not path.isdir(vitaSaves):
            os.mkdir(vitaSaves)
        
        # Create the config.yml file if it doesn't exist
        vita3kymlconfig = {}
        if os.path.isfile(vitaConfigFile):
            with open(vitaConfigFile, 'r') as stream:
                vita3kymlconfig = yaml.safe_load(stream)

        if vita3kymlconfig is None:
            vita3kymlconfig = {}
        
        # [Emulator configuration options]
        # Set the renderer
        if system.isOptSet("vita3k_gfxbackend"):
            vita3kymlconfig["backend-renderer"] = system.config["vita3k_gfxbackend"]
        else:
            vita3kymlconfig["backend-renderer"] = "OpenGL"
        
        # Set the resolution multiplier
        if system.isOptSet("vita3k_resolution"):
            vita3kymlconfig["resolution-multiplier"] = system.config["vita3k_resolution"]
        else:
            vita3kymlconfig["resolution-multiplier"] = 1        
        
        # Set FXAA
        if system.isOptSet("vita3k_fxaa"):
            vita3kymlconfig["enable-fxaa"] = system.config["vita3k_fxaa"]
        else:
            vita3kymlconfig["enable-fxaa"] = False
        
        # Set VSync
        if system.isOptSet("vita3k_vsync"):
            vita3kymlconfig["v-sync"] = system.config["vita3k_vsync"]
        else:
            vita3kymlconfig["v-sync"] = True        

        with open(vitaConfigFile, 'w') as file:
            documents = yaml.safe_dump(vita3kymlconfig, file, default_flow_style=False)
        
        # Simplify the rom name (strip the directory & extension)
        begin, end = rom.find('['), rom.rfind(']')
        smplromname = rom[begin+1: end]
        commandArray = ["/usr/bin/vita3k/Vita3K", "-F", "-c", vitaConfigFile, "-r", smplromname]

        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
            })
    
    # Show mouse for touchscreen actions
    def getMouseMode(self, config):
        return True
