#!/usr/bin/env python
import Command
from generators.Generator import Generator
import controllersConfig
import configparser
import os
import shutil
import batoceraFiles

class DXX_RebirthGenerator(Generator):

    def generate(self, system, rom, playersControllers, guns, wheels, gameResolution):
        
        directory = os.path.dirname(rom)

        if os.path.splitext(rom)[1] == ".d1x":
            dxx_rebirth = "d1x-rebirth"
        elif os.path.splitext(rom)[1] == ".d2x":
            dxx_rebirth = "d2x-rebirth"
        
        ## Configuration
        rebirthConfigDir = batoceraFiles.CONF + "/" + dxx_rebirth
        rebirthConfigFile = rebirthConfigDir + "/descent.cfg"
        
        if not os.path.exists(rebirthConfigDir):
            os.makedirs(rebirthConfigDir)
        
        # Check if the file exists
        if os.path.isfile(rebirthConfigFile):
            # Read the contents of the file
            with open(rebirthConfigFile, 'r') as file:
                lines = file.readlines()
            
            # Modify the values of ResolutionX and ResolutionY
            for i, line in enumerate(lines):
                if line.startswith('ResolutionX='):
                    lines[i] = f'ResolutionX={gameResolution["width"]}\n'
                elif line.startswith('ResolutionY='):
                    lines[i] = f'ResolutionY={gameResolution["height"]}\n'
            
            # Write the modified contents back to the file
            with open(rebirthConfigFile, 'w') as file:
                file.writelines(lines)
        
        else:
            # File doesn't exist, create it with default values
            with open(rebirthConfigFile, 'w') as file:
                file.write(f'ResolutionX={gameResolution["width"]}\n')
                file.write(f'ResolutionY={gameResolution["height"]}\n')
        
        commandArray = [dxx_rebirth, "-hogdir", directory]
        
        return Command.Command(
            array=commandArray,
            env={
                "XDG_CONFIG_HOME":batoceraFiles.CONF,
                "SDL_GAMECONTROLLERCONFIG":controllersConfig.generateSdlGameControllerConfig(playersControllers)
            }
        )
    
    # Show mouse for menu / play actions
    def getMouseMode(self, config):
        return True

    def getInGameRatio(self, config, gameResolution, rom):
        return 16/9
