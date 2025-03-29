from __future__ import annotations

from typing import TYPE_CHECKING, Final

from ... import Command
from ...batoceraPaths import CONFIGS
from ...utils.configparser import CaseSensitiveConfigParser
from ..Generator import Generator

if TYPE_CHECKING:
    from pathlib import Path

    from ...types import HotkeysContext

_CONFIG_DIR: Final = CONFIGS / 'dosbox'
# Use a separate file from dosbox.conf to avoid overwriting by dosbox
_CUSTOM_CONFIG: Final = _CONFIG_DIR / 'dosbox-custom.conf'

class DosBoxGenerator(Generator):

    # Main entry of the module
    # Return command
    def generate(self, system, rom, playersControllers, metadata, esmetadata, guns, wheels, gameResolution):
        # Find rom path
        batFile = rom / "dosbox.bat"
        gameConfFile = rom / "dosbox.cfg"

        # configuration file
        iniSettings = CaseSensitiveConfigParser(interpolation=None)

        if _CUSTOM_CONFIG.exists():
            iniSettings.read(_CUSTOM_CONFIG)

        # section sdl
        if not iniSettings.has_section("sdl"):
            iniSettings.add_section("sdl")
        iniSettings.set("sdl", "output", "opengl")

        # section cpu
        if not iniSettings.has_section("cpu"):
            iniSettings.add_section("cpu")

        iniSettings.set("cpu", "core", system.config.get("dosbox_cpu_core", "auto"))
        iniSettings.set("cpu", "cputype", system.config.get("dosbox_cpu_cputype", "auto"))
        iniSettings.set("cpu", "cycles", system.config.get("dosbox_cpu_cycles", "auto"))

        # save
        with _CUSTOM_CONFIG.open('w') as config:
            iniSettings.write(config)

        commandArray: list[str | Path] = [
            '/usr/bin/dosbox',
            "-fullscreen",
            # This loads _CONFIG_DIR / dosbox.conf
            "-userconf",
            "-exit",
            batFile,
            "-c", f"""set ROOT={rom}""",
        ]

        if gameConfFile.exists():
            # Then load gameConfFile if it exists
            commandArray.extend(['-conf', gameConfFile])

        commandArray.extend([
            # Then load _CUSTOM_CONFIG after all the others
            "-conf", _CUSTOM_CONFIG
        ])

        return Command.Command(array=commandArray)

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "dosbox",
            "keys": { "exit": ["KEY_LEFTCTRL", "KEY_F9"] }
        }
