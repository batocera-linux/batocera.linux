from __future__ import annotations

import shutil
from pathlib import Path
from typing import TYPE_CHECKING, Final

from ... import Command
from ...batoceraPaths import CONFIGS, SCREENSHOTS, mkdir_if_not_exists
from ...controller import generate_sdl_game_controller_config
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext

CONFIG_DIR: Final = CONFIGS / 'sdlpop'
SCREENSHOTS_DIR: Final = SCREENSHOTS / 'sdlpop'
SYSTEM_DIR: Final = Path('/usr/share/sdlpop')

USER_CONFIG: Final = CONFIG_DIR / 'SDLPoP.cfg'
USER_INI: Final = CONFIG_DIR / 'SDLPoP.ini'
SYSTEM_CONFIG: Final = SYSTEM_DIR / 'SDLPoP.cfg'
SYSTEM_INI: Final = SYSTEM_DIR / 'SDLPoP.ini'

class SdlPopGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "sdlpop",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"], "menu": "KEY_ESC", "pause": "KEY_ESC", "save_state": "KEY_F6", "restore_state": "KEY_F9" }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        commandArray = ["SDLPoP"]

        # create sdlpop config directory
        mkdir_if_not_exists(CONFIG_DIR)
        if not USER_CONFIG.exists():
            shutil.copyfile(SYSTEM_DIR / 'cfg' / 'SDLPoP.cfg', USER_CONFIG)
        if not USER_INI.exists():
            shutil.copyfile(SYSTEM_DIR / 'cfg' / 'SDLPoP.ini', USER_INI)
        # symbolic link cfg files
        if not SYSTEM_CONFIG.exists():
            SYSTEM_CONFIG.symlink_to(USER_CONFIG)
        if not SYSTEM_INI.exists():
            SYSTEM_INI.symlink_to(USER_INI)
        # symbolic link screenshot folder too
        if not SCREENSHOTS_DIR.exists():
            SCREENSHOTS_DIR.mkdir(parents=True)
            (SYSTEM_DIR / 'screenshots').symlink_to(SCREENSHOTS_DIR, target_is_directory=True)

        # pad number
        nplayer = 1
        for playercontroller, pad in sorted(playersControllers.items()):
            if nplayer == 1:
                commandArray.append(f"joynum={pad.index}")
            nplayer += 1

        return Command.Command(array=commandArray,env={
            "SDL_GAMECONTROLLERCONFIG": generate_sdl_game_controller_config(playersControllers)
        })
