#!/usr/bin/env python
import Command
import batoceraFiles
from generators.Generator import Generator
import controllersConfig
import os.path
import glob

class ScummVMGenerator(Generator):  
    # Main entry of the module
    # Configure mupen and return a command
    def generate(self, system, rom, playersControllers, guns, gameResolution):
        # crete /userdata/roms/scummvm/extras folder if it doesn't exist
        if not os.path.exists('/userdata/roms/scummvm/extras'):
            os.makedirs('/userdata/roms/scummvm/extras')
        
        # Find rom path
        if os.path.isdir(rom):
          # rom is a directory: must contains a <game name>.scummvm file
          romPath = rom
          romFile = glob.glob(romPath + "/*.scummvm")[0]
          romName = os.path.splitext(os.path.basename(romFile))[0]
        else:
          # rom is a file: split in directory and file name
          romPath = os.path.dirname(rom)
          # Get rom name without extension
          romName = os.path.splitext(os.path.basename(rom))[0]

        # pad number
        nplayer = 1
        id = 0
        for playercontroller, pad in sorted(playersControllers.items()):
            if nplayer == 1:
                id=pad.index
            nplayer += 1

        commandArray = [batoceraFiles.batoceraBins[system.config['emulator']],
                        "-f",
                        f"--joystick={id}",
                        "--screenshotspath="+batoceraFiles.screenshotsDir, 
                        "--extrapath=/userdata/roms/scummvm/extras",
                        "--savepath="+batoceraFiles.scummvmSaves,
                        "--path=""{}""".format(romPath)]
        commandArray.append(f"""{romName}""")

        return Command.Command(array=commandArray,env={
            "SDL_GAMECONTROLLERCONFIG": controllersConfig.generateSdlGameControllerConfig(playersControllers)
        })
