from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Final

from ... import Command
from ...batoceraPaths import CONFIGS, ROMS, SAVES, mkdir_if_not_exists
from ...controller import generate_sdl_game_controller_config
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext

_logger = logging.getLogger(__name__)

_CATACOMBGL_CONFIG: Final = CONFIGS / "CatacombGL"
_CATACOMBGL_SAVES: Final = SAVES / "CatacombGL"
_CATACOMBGL_ROMS: Final = ROMS / "catacomb"

class CatacombGLGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "catacombgl",
            "keys": {
                "exit": ["KEY_LEFTALT", "KEY_F4"],
                "save_state": ["KEY_F3"],
                "restore_state": ["KEY_F4"],
                "menu": "KEY_ESC"
            },
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        mkdir_if_not_exists(_CATACOMBGL_SAVES)
        # Path to the ini file
        _CATACOMBGL_CONFIG_FILE = _CATACOMBGL_CONFIG / "CatacombGL.ini"
        _CATACOMBGL_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)

        # Check if the ini file exists, and if not, create and adjust it
        if not _CATACOMBGL_CONFIG_FILE.exists():
            _logger.debug("CatacombGL.ini not found, creating the file.")
            _CATACOMBGL_CONFIG_FILE.touch()  # Create the file if it doesn't exist

        # Define the paths to be added or adjusted in the ini file
        required_paths = {
            "pathabyssv113": _CATACOMBGL_ROMS / "Abyss_sw13",
            "pathabyssv124": _CATACOMBGL_ROMS / "Abyss",
            "patharmageddonv102": _CATACOMBGL_ROMS / "Armageddon",
            "pathapocalypsev101": _CATACOMBGL_ROMS / "Apocalypse",
            "pathcatacomb3dv122": _CATACOMBGL_ROMS / "Cat3D",
            "screenmode": "fullscreen",
            "WindowedScreenWidth": str(gameResolution["width"]),
            "WindowedScreenHeight": str(gameResolution["height"])
        }

        # Read the existing file content
        ini_content = _CATACOMBGL_CONFIG_FILE.read_text().splitlines() if _CATACOMBGL_CONFIG_FILE.exists() else []
        ini_dict = {line.split("=")[0]: line.split("=")[1] for line in ini_content if "=" in line}

        # Update or add required paths
        with _CATACOMBGL_CONFIG_FILE.open("w") as ini_file:
            for key, value in required_paths.items():
                ini_dict[key] = value
            for key, value in ini_dict.items():
                ini_file.write(f"{key}={value}\n")

        # Run command
        commandArray = ["/usr/bin/CatacombGL", "--savedir", _CATACOMBGL_SAVES]

        # Version
        rom_file_name = Path(rom).name.lower()

        # Check and extend the command array with specific arguments
        for keyword, argument in {
            "abyss": "--abyss",
            "abyss_sw13": "--abyss_sw13",
            "descent": "--descent",
            "armageddon": "--armageddon",
            "apocalypse": "--apocalypse",
        }.items():
            if keyword in rom_file_name:
                _logger.debug("Version requested: %s", keyword)
                commandArray.append(argument)

        # Return the configured command
        return Command.Command(
            array=commandArray,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_game_controller_config(playersControllers),
                "SDL_JOYSTICK_HIDAPI": "0"
            }
        )

    def getInGameRatio(self, config, gameResolution, rom):
        return 16 / 9
