#!/usr/bin/env python
import Command
import batoceraFiles
from generators.Generator import Generator
import os.path
import glob


class DosBoxGenerator(Generator):

    def getResolutionMode(self, config):
        return 'default'
    
    # Main entry of the module
    # Return command
    def generate(self, system, rom, playersControllers, gameResolution):
        # Find rom path
        gameDir = rom
        batFile = gameDir + "/dosbox.bat"
        gameConfFile = gameDir + "/dosbox.cfg"
           
        commandArray = [batoceraFiles.batoceraBins[system.config['emulator']],
			"-fullscreen",
			"-userconf", 
			"-exit", 
			f"""{batFile}""",
			"-c", f"""set ROOT={gameDir}"""]
        if os.path.isfile(gameConfFile):
            commandArray.append("-conf")
            commandArray.append(f"""{gameConfFile}""")
        else:
            commandArray.append("-conf")
            commandArray.append(f"""{batoceraFiles.dosboxConfig}""")

        return Command.Command(array=commandArray)
