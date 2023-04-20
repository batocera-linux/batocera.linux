#!/usr/bin/env python
import Command
import controllersConfig
import batoceraFiles
from . import moonlightConfig
from generators.Generator import Generator
import shutil
import os.path

class MoonlightGenerator(Generator):

    def getResolutionMode(self, config):
        return 'default'
    
    # Main entry of the module
    # Configure fba and return a command
    def generate(self, system, rom, playersControllers, guns, gameResolution):
        moonlightConfig.generateMoonlightConfig(system)
        gameName,confFile = self.getRealGameNameAndConfigFile(rom)
        commandArray = [batoceraFiles.batoceraBins[system.config['emulator']], 'stream','-config',  confFile]
        commandArray.append('-app')
        commandArray.append(gameName)
        commandArray.append('-debug')
        return Command.Command(
            array=commandArray,
            env={
                "XDG_DATA_DIRS": batoceraFiles.CONF,
                "SDL_GAMECONTROLLERCONFIG": controllersConfig.generateSdlGameControllerConfig(playersControllers),
                "SDL_JOYSTICK_HIDAPI": "0"
                }
        )

    def getRealGameNameAndConfigFile(self, rom):
        # Rom's basename without extension
        romName = os.path.splitext(os.path.basename(rom))[0]
        # find the real game name
        f = open(batoceraFiles.moonlightGamelist, 'r')
        gfeGame = None
        for line in f:
            try:
                gfeRom, gfeGame, confFile = line.rstrip().split(';')
                #confFile = confFile.rstrip()
            except:
                gfeRom, gfeGame = line.rstrip().split(';')
                confFile = batoceraFiles.moonlightStagingConfigFile
            #If found
            if gfeRom == romName:
                # return it
                f.close()
                return [gfeGame, confFile]
        # If nothing is found (old gamelist file format ?)
        return [gfeGame, batoceraFiles.moonlightStagingConfigFile]
