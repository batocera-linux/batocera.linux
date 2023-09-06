#!/usr/bin/env python
import Command
import batoceraFiles
from generators.Generator import Generator
import os.path
import glob
from . import viceConfig
from . import viceControllers
import controllersConfig
import zipfile

class ViceGenerator(Generator):

    def getResolutionMode(self, config):
        return 'default'
    
    # Main entry of the module
    # Return command
    def generate(self, system, rom, playersControllers, guns, wheels, gameResolution):

        if not os.path.exists(os.path.dirname(batoceraFiles.viceConfig)):
            os.makedirs(os.path.dirname(batoceraFiles.viceConfig))

        # configuration file
        viceConfig.setViceConfig(batoceraFiles.viceConfig, system, guns, rom)

        # controller configuration
        viceControllers.generateControllerConfig(system, batoceraFiles.viceConfig, playersControllers)

        commandArray = [batoceraFiles.batoceraBins[system.config['emulator']] + system.config['core']]
        # Determine the way to launch roms based on extension type
        rom_extension = os.path.splitext(rom)[1].lower()
        # determine extension if a zip file
        if rom_extension == ".zip":
            with zipfile.ZipFile(rom, "r") as zip_file:
                for zip_info in zip_file.infolist():
                    rom_extension = os.path.splitext(zip_info.filename)[1]
        
        # TODO - add some logic for various extension types
        
        commandArray.append(rom)

        return Command.Command(
            array=commandArray,
            env={
                "XDG_CONFIG_HOME":batoceraFiles.CONF,
                "SDL_GAMECONTROLLERCONFIG": controllersConfig.generateSdlGameControllerConfig(playersControllers),
                "SDL_JOYSTICK_HIDAPI": "0"
            }
        )
