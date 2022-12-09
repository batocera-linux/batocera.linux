#!/usr/bin/env python
import Command
import batoceraFiles
from generators.Generator import Generator
import os.path
import glob


class DosBoxStagingGenerator(Generator):

    # Main entry of the module
    # Return command
    def generate(self, system, rom, playersControllers, guns, gameResolution):
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
            commandArray.append(f"""{batoceraFiles.dosboxStagingConfig}""")

        return Command.Command(array=commandArray)
