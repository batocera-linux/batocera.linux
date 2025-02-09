from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from ... import Command
from ...batoceraPaths import CONFIGS
from ..Generator import Generator
from ...utils.configparser import CaseSensitiveConfigParser

if TYPE_CHECKING:
    from ...types import HotkeysContext

_CONFIG_DIR: Final = CONFIGS / 'dosbox'
_CONFIG: Final = _CONFIG_DIR / 'dosbox.conf'

class DosBoxGenerator(Generator):

    # Main entry of the module
    # Return command
    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        # Find rom path
        gameDir = Path(rom)
        batFile = gameDir / "dosbox.bat"
        gameConfFile = gameDir / "dosbox.cfg"
        # copy gamedir configs to custom.conf
        customConfFile = _CONFIG_DIR / 'dosbox-custom.conf'

        configFile = _CONFIG
        if gameConfFile.is_file():
            shutil.copy2(configFile, customConfFile)
        else:
            # empty custom.conf when there is nothing from game directory
            open(customConfFile, 'w').close()

        # configuration file
        iniSettings = CaseSensitiveConfigParser(interpolation=None)
        if configFile.exists():
            iniSettings.read(configFile)

        # section sdl
        if not iniSettings.has_section("sdl"):
            iniSettings.add_section("sdl")
        iniSettings.set("sdl", "output", "opengl")

        # section cpu
        if not iniSettings.has_section("cpu"):
            iniSettings.add_section("cpu")

        if system.isOptSet('dosbox_cpu_core'):
            iniSettings.set("cpu", "core", system.config["dosbox_cpu_core"])
        else:
            iniSettings.set("cpu", "core", "auto")

        if system.isOptSet('dosbox_cpu_cputype'):
            iniSettings.set("cpu", "cputype", system.config["dosbox_cpu_cputype"])
        else:
            iniSettings.set("cpu", "cputype", "auto")

        if system.isOptSet('dosbox_cpu_cycles'):
            iniSettings.set("cpu", "cycles", system.config["dosbox_cpu_cycles"])
        else:
            iniSettings.set("cpu", "cycles", "auto")

        # save
        with configFile.open('w') as config:
            iniSettings.write(config)

        commandArray: list[str | Path] = [
            '/usr/bin/dosbox',
            "-fullscreen",
            "-userconf",
            "-exit",
            batFile,
            "-c", f"""set ROOT={gameDir}""",
            "-conf", customConfFile
        ]

        return Command.Command(array=commandArray)

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "dosbox",
            "keys": { "exit": ["KEY_LEFTCTRL", "KEY_F9"] }
        }
