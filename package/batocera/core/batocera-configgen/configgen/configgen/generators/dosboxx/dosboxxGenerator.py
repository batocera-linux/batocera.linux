from __future__ import annotations

import shutil
from typing import TYPE_CHECKING, Final

from ... import Command
from ...batoceraPaths import CONFIGS
from ...utils.configparser import CaseSensitiveConfigParser
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext

_CONFIG_DIR: Final = CONFIGS / 'dosbox'
_CONFIG: Final = _CONFIG_DIR / 'dosboxx.conf'

class DosBoxxGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        # Find rom path
        gameConfFile = rom / "dosbox.cfg"

        configFile = _CONFIG
        if gameConfFile.is_file():
            configFile = gameConfFile

        # configuration file
        iniSettings = CaseSensitiveConfigParser(interpolation=None)

        # copy config file to custom config file to avoid overwritting by dosbox-x
        customConfFile = _CONFIG_DIR / 'dosboxx-custom.conf'

        if configFile.exists():
            shutil.copy2(configFile, customConfFile)
            iniSettings.read(customConfFile)

        # sections
        if not iniSettings.has_section("sdl"):
            iniSettings.add_section("sdl")
        iniSettings.set("sdl", "output", "opengl")

        # save
        with customConfFile.open('w') as config:
            iniSettings.write(config)

        # -fullscreen removed as it crashes on N2
        commandArray = ['/usr/bin/dosbox-x',
                        "-exit"]

        # Find autoexe file
        autoexecFile = rom / "dosbox.aut"
        if autoexecFile.exists():
            # Read dosbox.aut and append it to the custom config file
            with customConfFile.open('a+') as f1:
                f1.write(autoexecFile.read_text())

            # Setting the defaultdir to the rom dir.
            # This way we can use relative paths to the rom directory
            # in dosbox.auto
            commandArray.extend([
                        "-defaultdir", f"""{rom!s}"""])
        else:
            # Otherwise, mount the rom directory as c: and run dosbox.bat
            commandArray.extend([
                        "-c", f"""mount c {rom!s}""",
                        "-c", "c:",
                        "-c", "dosbox.bat"])

        commandArray.extend([
                        "-fastbioslogo",
                        "-conf", f"{customConfFile!s}"])

        return Command.Command(array=commandArray, env={"XDG_CONFIG_HOME":CONFIGS})

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "dosboxx",
            "keys": { "exit": ["KEY_LEFTCTRL", "KEY_F9"] }
        }
