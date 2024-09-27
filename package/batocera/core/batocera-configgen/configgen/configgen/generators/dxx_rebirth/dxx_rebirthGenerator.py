import os

from ... import batoceraFiles
from ... import Command
from ... import controllersConfig
from ..Generator import Generator

class DXX_RebirthGenerator(Generator):

    def getHotkeysContext(self):
        return {
            "name": "dxx_rebirth",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"], "menu": "KEY_F2", "save_state": ["KEY_LEFTALT", "KEY_F2"], "restore_state": ["KEY_LEFTALT", "KEY_LEFTSHIFT", "KEY_F2"] }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

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

            for i, line in enumerate(lines):
                # set resolution
                if line.startswith('ResolutionX='):
                    lines[i] = f'ResolutionX={gameResolution["width"]}\n'
                elif line.startswith('ResolutionY='):
                    lines[i] = f'ResolutionY={gameResolution["height"]}\n'
                # fullscreen
                if line.startswith('WindowMode='):
                    lines[i] = f'WindowMode=0\n'
                # vsync
                if line.startswith('VSync='):
                    if system.isOptSet("rebirth_vsync"):
                        lines[i] = f'VSync={system.config["rebirth_vsync"]}\n'
                    else:
                        lines[i] = f'VSync=0\n'
                # texture filtering
                if line.startswith('TexFilt='):
                    if system.isOptSet("rebirth_filtering"):
                        lines[i] = f'TexFilt={system.config["rebirth_filtering"]}\n'
                    else:
                        lines[i] = f'TexFilt=0\n'
                # anisotropy
                if line.startswith('TexAnisotropy='):
                    if system.isOptSet("rebirth_anisotropy"):
                        lines[i] = f'TexAnisotropy={system.config["rebirth_anisotropy"]}\n'
                    else:
                        lines[i] = f'TexAnisotropy=0\n'
                # 4x multisampling
                if line.startswith('Multisample='):
                    if system.isOptSet("rebirth_multisample"):
                        lines[i] = f'Multisample={system.config["rebirth_multisample"]}\n'
                    else:
                        lines[i] = f'Multisample=0\n'

            with open(rebirthConfigFile, 'w') as file:
                file.writelines(lines)

        else:
            # File doesn't exist, create it with some default values
            with open(rebirthConfigFile, 'w') as file:
                file.write(f'ResolutionX={gameResolution["width"]}\n')
                file.write(f'ResolutionY={gameResolution["height"]}\n')
                file.write(f'WindowMode=0\n')
                file.write(f'VSync=0\n')
                file.write(f'TexFilt=0\n')
                file.write(f'TexAnisotropy=0\n')
                file.write(f'Multisample=0\n')

        commandArray = [dxx_rebirth, "-hogdir", directory]

        return Command.Command(
            array=commandArray,
            env={
                "SDL_GAMECONTROLLERCONFIG":controllersConfig.generateSdlGameControllerConfig(playersControllers)
            }
        )

    # Show mouse for menu / play actions
    def getMouseMode(self, config, rom):
        return True

    def getInGameRatio(self, config, gameResolution, rom):
        return 16/9
