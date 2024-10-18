from __future__ import annotations

from typing import TYPE_CHECKING

from ... import Command
from ...batoceraPaths import CONFIGS, SAVES
from ...controller import generate_sdl_game_controller_config
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext


class DevilutionXGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        configDir = CONFIGS / 'devilutionx'
        saveDir = SAVES / 'devilutionx'

        configDir.mkdir(parents=True, exist_ok=True)
        saveDir.mkdir(parents=True, exist_ok=True)

        commandArray = ['devilutionx', '--data-dir', '/userdata/roms/devilutionx',
                        '--config-dir', configDir, '--save-dir', saveDir]
        if rom.endswith('hellfire.mpq'):
            commandArray.append('--hellfire')
        elif rom.endswith('spawn.mpq'):
            commandArray.append('--spawn')
        else:
            commandArray.append('--diablo')

        if system.isOptSet('showFPS') and system.getOptBoolean('showFPS') == True:
            commandArray.append('-f')
        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': generate_sdl_game_controller_config(playersControllers)
            })

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "devilutionx",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"], "menu": "KEY_ESC", "pause": "KEY_ESC", "save_state": "KEY_F2", "restore_state": "KEY_F3" }
        }
