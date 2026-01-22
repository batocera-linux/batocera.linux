from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
from configparser import ConfigParser

from ... import Command
from ...batoceraPaths import CONFIGS, HOME
from ...controller import generate_sdl_game_controller_config, write_sdl_controller_db
from ...exceptions import BatoceraException
from ..Generator import Generator
from . import moonlightConfig
from .moonlightPaths import MOONLIGHT_GAME_LIST, MOONLIGHT_STAGING_CONFIG

if TYPE_CHECKING:
    from ...types import HotkeysContext


class MoonlightGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "moonlight",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"] }
        }

    def getResolutionMode(self, config):
        return 'default'

    def get_moonlight_executable(self):
        client_executables = [
            '/usr/bin/moonlight-qt',
        ]
        for executable in client_executables:
            path = Path(executable)
            if path.is_file():
                return executable
        return None

    def get_moonlight_host(self):
        try:
            config_path = HOME / ".config/Moonlight Game Streaming Project/Moonlight.conf"
            config = ConfigParser()
            config.read(config_path)
            host = config["hosts"]["1\\manualaddress"]
            return host
        except:
            return None

    # Main entry of the module
    # Configure fba and return a command
    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        executable = self.get_moonlight_executable()
        if executable is not None and executable.endswith("qt"):
            command = self.generate_qt(system, rom, playersControllers, metadata, guns, wheels, gameResolution)
        else:
            command = self.generate_embedded(system, rom, playersControllers, metadata, guns, wheels, gameResolution)

        return Command.Command(
            array=command,
            env={
                "XDG_DATA_DIRS": CONFIGS,
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_game_controller_config(playersControllers),
                "SDL_JOYSTICK_HIDAPI": "0"
            }
        )

    def generate_qt(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        commandArray = ['/usr/bin/moonlight-qt']

        host = self.get_moonlight_host()

        if not host:
            return commandArray


        # resolution
        match system.config.get("moonlight_resolution"):
            case "1":
                commandArray.append('--1080')
            case "2":
                commandArray.append('--4K')
            case _:
                commandArray.append('--720')

        # framerate
        match system.config.get("moonlight_framerate"):
            case "0":
                framerate = '30'
            case "2":
                framerate = '120'
            case _:
                framerate = '60'
        commandArray.append('--fps')
        commandArray.append(framerate)

        # bitrate
        match system.config.get("moonlight_bitrate"):
            case "0":
                bitrate = '5000'
            case "1":
                bitrate = '10000'
            case "2":
                bitrate = '20000'
            case "3":
                bitrate = '50000'
            case _:
                bitrate = None  # Moonlight default
        if bitrate is not None:
            commandArray.append('--bitrate')
            commandArray.append(bitrate)

        # quit remote app on exit
        if system.config.get("moonlight_quitapp"):
            commandArray.append('--quit-after')
        else:
            commandArray.append('--no-quit-after')

        # host
        if host:
            commandArray.append('stream')
            commandArray.append(host)

        # app
        app = rom.read_text().rstrip()
        commandArray.append(app)

        return commandArray

    def generate_embedded(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        moonlightConfig.generateMoonlightConfig(system)
        gameName, confFile = self.getRealGameNameAndConfigFile(rom)
        commandArray = ['/usr/bin/moonlight', 'stream','-config',  confFile]
        commandArray.append('-app')
        commandArray.append(gameName)
        commandArray.append('-debug')

        # write our own gamecontrollerdb.txt file before launching the game
        dbfile = "/usr/share/moonlight/gamecontrollerdb.txt"
        write_sdl_controller_db(playersControllers, dbfile)

        return commandArray

    def getRealGameNameAndConfigFile(self, rom: Path) -> tuple[str, Path]:
        # find the real game name
        f = MOONLIGHT_GAME_LIST.open()
        for line in f:
            try:
                gfeRom, gfeGame, confFileString = line.rstrip().split(';')
                confFile = Path(confFileString)
                #confFile = confFile.rstrip()
            except Exception:
                gfeRom, gfeGame = line.rstrip().split(';')
                confFile = MOONLIGHT_STAGING_CONFIG
            #If found
            if gfeRom == rom.stem:
                # return it
                f.close()
                return gfeGame, confFile

        raise BatoceraException(f'{rom.stem} was not found in the Moonlight game list')
