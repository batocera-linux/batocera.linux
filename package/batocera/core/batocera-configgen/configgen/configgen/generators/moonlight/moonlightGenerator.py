from __future__ import annotations

from pathlib import Path

from ... import Command, controllersConfig
from ...batoceraPaths import CONFIGS
from ..Generator import Generator
from . import moonlightConfig
from .moonlightPaths import MOONLIGHT_GAME_LIST, MOONLIGHT_STAGING_CONFIG


class MoonlightGenerator(Generator):

    def getHotkeysContext(self):
        return {
            "name": "moonlight",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"] }
        }

    def getResolutionMode(self, config):
        return 'default'

    # Main entry of the module
    # Configure fba and return a command
    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        moonlightConfig.generateMoonlightConfig(system)
        gameName, confFile = self.getRealGameNameAndConfigFile(Path(rom))
        commandArray = ['/usr/bin/moonlight', 'stream','-config',  confFile]
        commandArray.append('-app')
        commandArray.append(gameName)
        commandArray.append('-debug')

        # write our own gamecontrollerdb.txt file before launching the game
        dbfile = "/usr/share/moonlight/gamecontrollerdb.txt"
        controllersConfig.writeSDLGameDBAllControllers(playersControllers, dbfile)

        return Command.Command(
            array=commandArray,
            env={
                "XDG_DATA_DIRS": CONFIGS,
                "SDL_GAMECONTROLLERCONFIG": controllersConfig.generateSdlGameControllerConfig(playersControllers),
                "SDL_JOYSTICK_HIDAPI": "0"
            }
        )

    def getRealGameNameAndConfigFile(self, rom: Path) -> tuple[str | None, Path]:
        # find the real game name
        f = MOONLIGHT_GAME_LIST.open()
        gfeGame = None
        for line in f:
            try:
                gfeRom, gfeGame, confFileString = line.rstrip().split(';')
                confFile = Path(confFileString)
                #confFile = confFile.rstrip()
            except:
                gfeRom, gfeGame = line.rstrip().split(';')
                confFile = MOONLIGHT_STAGING_CONFIG
            #If found
            if gfeRom == rom.stem:
                # return it
                f.close()
                return gfeGame, confFile
        # If nothing is found (old gamelist file format ?)
        return gfeGame, MOONLIGHT_STAGING_CONFIG
