#!/usr/bin/env python
import Command
import controllersConfig
import batoceraFiles
import moonlightConfig
from generators.Generator import Generator
import shutil
import os.path


class MoonlightGenerator(Generator):

    def getResolutionMode(self, config):
        return 'default'
    
    # Main entry of the module
    # Configure fba and return a command
    def generate(self, system, rom, playersControllers, gameResolution):
        moonlightConfig.generateMoonlightConfig()
        outputFile = batoceraFiles.moonlightCustom + '/gamecontrollerdb.txt'
        configFile = controllersConfig.generateSDLGameDBAllControllers(playersControllers, outputFile)
        gameName,confFile = self.getRealGameNameAndConfigFile(rom)
        commandArray = [batoceraFiles.batoceraBins[system.config['emulator']], 'stream','-config',  confFile]
        commandArray.append('-app')
        commandArray.append(gameName)
        return Command.Command(array=commandArray, env={"XDG_DATA_DIRS": batoceraFiles.CONF})

    def getRealGameNameAndConfigFile(self, rom):
        # Rom's basename without extension
        romName = os.path.splitext(os.path.basename(rom))[0]
        # find the real game name
        f = open(batoceraFiles.moonlightGamelist, 'r')
        for line in f:
            try:
                gfeRom, gfeGame, confFile = line.rstrip().split(';')
                #confFile = confFile.rstrip()
            except:
                gfeRom, gfeGame = line.rstrip().split(';')
                confFile = batoceraFiles.moonlightConfigFile
            #If found
            if gfeRom == romName:
                # return it
                f.close()
                return [gfeGame, confFile]
        # If nothing is found (old gamelist file format ?)
        return [gfeGame, batoceraFiles.moonlightConfigFile]
