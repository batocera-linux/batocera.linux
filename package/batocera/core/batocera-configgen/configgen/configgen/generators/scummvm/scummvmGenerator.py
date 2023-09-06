#!/usr/bin/env python
import Command
import batoceraFiles
from generators.Generator import Generator
import controllersConfig
import os.path
import glob

class ScummVMGenerator(Generator):  

    def generate(self, system, rom, playersControllers, guns, wheels, gameResolution):
        # crete /userdata/bios/scummvm/extra folder if it doesn't exist
        if not os.path.exists('/userdata/bios/scummvm/extra'):
            os.makedirs('/userdata/bios/scummvm/extra')
        
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

        commandArray = [batoceraFiles.batoceraBins[system.config['emulator']], "-f"]
        
        # set the resolution
        window_width = str(gameResolution["width"])
        window_height = str(gameResolution["height"])
        commandArray.append(f"--window-size={window_width},{window_height}")

        ## user options

        # scale factor
        if system.isOptSet("scumm_scale"):
            commandArray.append(f"--scale-factor={system.config['scumm_scale']}")
        else:
            commandArray.append("--scale-factor=3")

        # sclaer mode
        if system.isOptSet("scumm_scaler_mode"):
            commandArray.append(f"--scaler={system.config['scumm_scaler_mode']}")
        else:
            commandArray.append("--scaler=normal")
                
        #  stretch mode
        if system.isOptSet("scumm_stretch"):
            commandArray.append(f"--stretch-mode={system.config['scumm_stretch']}")
        else:
            commandArray.append("--stretch-mode=center")

        # renderer
        if system.isOptSet("scumm_renderer"):
            commandArray.append(f"--renderer={system.config['scumm_renderer']}")
        else:
            commandArray.append("--renderer=opengl")

        # language
        if system.isOptSet("scumm_language"):
            commandArray.extend(["-q", f"{system.config['scumm_language']}"])
        else:
            commandArray.extend(["-q", "en"])

        # logging
        commandArray.append("--logfile=/userdata/system/logs")

        commandArray.extend(
            [f"--joystick={id}",
            "--screenshotspath="+batoceraFiles.screenshotsDir,
            "--extrapath=/userdata/bios/scummvm/extra",
            "--savepath="+batoceraFiles.scummvmSaves,
            "--path=""{}""".format(romPath),
            f"""{romName}"""]
        )

        return Command.Command(
            array=commandArray, env={
                "SDL_GAMECONTROLLERCONFIG": controllersConfig.generateSdlGameControllerConfig(playersControllers)
            }
        )
    
    def getInGameRatio(self, config, gameResolution, rom):
        if ("scumm_stretch" in config and config["scumm_stretch"] == "fit_force_aspect") or ("scumm_stretch" in config and config["scumm_stretch"] == "pixel-perfect"):
            return 4/3
        return 16/9
