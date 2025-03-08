from __future__ import annotations

from typing import TYPE_CHECKING

from ... import Command
from ...batoceraPaths import CONFIGS, mkdir_if_not_exists
from ...controller import generate_sdl_game_controller_config
from ...exceptions import BatoceraException
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext


class DXX_RebirthGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "dxx_rebirth",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"], "menu": "KEY_F2", "pause": "KEY_F2", "save_state": ["KEY_LEFTALT", "KEY_F2"], "restore_state": ["KEY_LEFTALT", "KEY_LEFTSHIFT", "KEY_F2"] }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        if rom.suffix == ".d1x":
            dxx_rebirth = "d1x-rebirth"
        elif rom.suffix == ".d2x":
            dxx_rebirth = "d2x-rebirth"
        else:
            raise BatoceraException(f"Unknown rom type: {rom}")

        ## Configuration
        rebirthConfigDir = CONFIGS / dxx_rebirth
        rebirthConfigFile = rebirthConfigDir / "descent.cfg"

        mkdir_if_not_exists(rebirthConfigDir)

        # Check if the file exists
        if rebirthConfigFile.is_file():
            # Read the contents of the file
            with rebirthConfigFile.open('r') as file:
                lines = file.readlines()

            for i, line in enumerate(lines):
                # set resolution
                if line.startswith('ResolutionX='):
                    lines[i] = f'ResolutionX={gameResolution["width"]}\n'
                elif line.startswith('ResolutionY='):
                    lines[i] = f'ResolutionY={gameResolution["height"]}\n'
                # fullscreen
                if line.startswith('WindowMode='):
                    lines[i] = 'WindowMode=0\n'
                # vsync
                if line.startswith('VSync='):
                    if system.isOptSet("rebirth_vsync"):
                        lines[i] = f'VSync={system.config["rebirth_vsync"]}\n'
                    else:
                        lines[i] = 'VSync=0\n'
                # texture filtering
                if line.startswith('TexFilt='):
                    if system.isOptSet("rebirth_filtering"):
                        lines[i] = f'TexFilt={system.config["rebirth_filtering"]}\n'
                    else:
                        lines[i] = 'TexFilt=0\n'
                # anisotropy
                if line.startswith('TexAnisotropy='):
                    if system.isOptSet("rebirth_anisotropy"):
                        lines[i] = f'TexAnisotropy={system.config["rebirth_anisotropy"]}\n'
                    else:
                        lines[i] = 'TexAnisotropy=0\n'
                # 4x multisampling
                if line.startswith('Multisample='):
                    if system.isOptSet("rebirth_multisample"):
                        lines[i] = f'Multisample={system.config["rebirth_multisample"]}\n'
                    else:
                        lines[i] = 'Multisample=0\n'

            with rebirthConfigFile.open('w') as file:
                file.writelines(lines)

        else:
            # File doesn't exist, create it with some default values
            with rebirthConfigFile.open('w') as file:
                file.write(f'ResolutionX={gameResolution["width"]}\n')
                file.write(f'ResolutionY={gameResolution["height"]}\n')
                file.write('WindowMode=0\n')
                file.write('VSync=0\n')
                file.write('TexFilt=0\n')
                file.write('TexAnisotropy=0\n')
                file.write('Multisample=0\n')

        commandArray = [dxx_rebirth, "-hogdir", rom.parent]

        return Command.Command(
            array=commandArray,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_game_controller_config(playersControllers)
            }
        )

    # Show mouse for menu / play actions
    def getMouseMode(self, config, rom):
        return True

    def getInGameRatio(self, config, gameResolution, rom):
        return 16/9
