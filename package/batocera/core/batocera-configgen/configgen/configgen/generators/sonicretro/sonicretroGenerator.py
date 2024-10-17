from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import TYPE_CHECKING

from ... import Command
from ...controller import generate_sdl_game_controller_config
from ...utils.configparser import CaseSensitiveRawConfigParser
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext

class SonicRetroGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "sonicretro",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"], "menu": "KEY_ENTER", "pause": "KEY_ENTER" }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        rom_path = Path(rom)

        # Determine the emulator to use
        if rom_path.name.lower().endswith("son"):
            emu = "sonic2013"
        else:
            emu = "soniccd"

        iniFile = rom_path / "settings.ini"

        # Some code copied from Citra's generator and adapted.

        sonicButtons = {
            "Up":       "11",
            "Down":     "12",
            "Left":     "13",
            "Right":    "14",
            "A":        "0",
            "B":        "1",
            "C":        "2",
            "X":        "3",
            "Y":        "22",
            "Z":        "23",
            "L":        "9",
            "R":        "10",
            "Select":   "4",
            "Start":    "6"
        }

        sonicKeys = {
            "Up":       "82",
            "Down":     "81",
            "Left":     "80",
            "Right":    "79",
            "A":        "29",
            "B":        "27",
            "C":        "6",
            "X":        "4",
            "Y":        "22",
            "Z":        "7",
            "L":        "20",
            "R":        "8",
            "Start":    "40",
            "Select":   "43"
        }

        # ini file
        sonicConfig = CaseSensitiveRawConfigParser(strict=False)
        if iniFile.exists():
            iniFile.unlink()          # Force removing settings.ini
            sonicConfig.read(iniFile)

        # [Dev]
        if not sonicConfig.has_section("Dev"):
            sonicConfig.add_section("Dev")
        if system.isOptSet('devmenu') and system.config["devmenu"] == '1':
            sonicConfig.set("Dev", "DevMenu", "true")
        else:
            sonicConfig.set("Dev", "DevMenu", "false")
        sonicConfig.set("Dev", "EngineDebugMode", "false")
        if (emu == "sonic2013"):
            sonicConfig.set("Dev", "StartingCategory", "255")
            sonicConfig.set("Dev", "StartingScene", "255")
            sonicConfig.set("Dev", "StartingPlayer", "255")
            sonicConfig.set("Dev", "StartingSaveFile", "255")
        else:
            sonicConfig.set("Dev", "StartingCategory", "0")
            sonicConfig.set("Dev", "StartingScene", "0")
            sonicConfig.set("Dev", "UseSteamDir", "false")
        sonicConfig.set("Dev", "FastForwardSpeed", "8")
        if system.isOptSet('hqmode') and system.config["hqmode"] == '0':
            sonicConfig.set("Dev", "UseHQModes", "false")
        else:
            sonicConfig.set("Dev", "UseHQModes", "true")
        sonicConfig.set("Dev", "DataFile", "Data.rsdk")

        # [Game]
        if not sonicConfig.has_section("Game"):
            sonicConfig.add_section("Game")

        if (emu == "sonic2013"):
            if system.isOptSet('skipstart') and system.config["skipstart"] == '1':
                sonicConfig.set("Game", "SkipStartMenu", "true")
            else:
                sonicConfig.set("Game", "SkipStartMenu", "false")
        else:
            if system.isOptSet('spindash'):
                sonicConfig.set("Game", "OriginalControls", system.config["spindash"])
            else:
                sonicConfig.set("Game", "OriginalControls", "-1")
            sonicConfig.set("Game", "DisableTouchControls", "true")

        originsGameConfig = [
            # Sonic 1
            "5250b0e2effa4d48894106c7d5d1ad32",
            "5771433883e568715e7ac994bb22f5ed",
            # Sonic 2
            "f958285af4a09d2023b4e4f453691c4f",
            "9fe2dae0a8a2c7d8ef0bed639b3c749f",
            # Sonic CD
            "e723aab26026e4e6d4522c4356ef5a98",
        ]
        game_config_bin = rom_path / "Data" / "Game" / "GameConfig.bin"
        if game_config_bin.is_file() and self.__getMD5(game_config_bin) in originsGameConfig:
            sonicConfig.set("Game", "GameType", "1")

        if system.isOptSet('language'):
            sonicConfig.set("Game", "Language", system.config["language"])
        else:
            sonicConfig.set("Game", "Language", "0")

        # [Window]
        if not sonicConfig.has_section("Window"):
            sonicConfig.add_section("Window")

        sonicConfig.set("Window", "FullScreen", "true")
        sonicConfig.set("Window", "Borderless", "true")
        if system.isOptSet('vsync') and system.config["vsync"] == "0":
            sonicConfig.set("Window", "VSync", "false")
        else:
            sonicConfig.set("Window", "VSync", "true")
        if system.isOptSet('scalingmode'):
            sonicConfig.set("Window", "ScalingMode", system.config["scalingmode"])
        else:
            sonicConfig.set("Window", "ScalingMode", "2")
        sonicConfig.set("Window", "WindowScale", "2")
        sonicConfig.set("Window", "ScreenWidth", "424")
        sonicConfig.set("Window", "RefreshRate", "60")
        sonicConfig.set("Window", "DimLimit", "-1")

        # [Audio]
        if not sonicConfig.has_section("Audio"):
            sonicConfig.add_section("Audio")

        sonicConfig.set("Audio", "BGMVolume", "1.000000")
        sonicConfig.set("Audio", "SFXVolume", "1.000000")

        # [Keyboard 1]
        if not sonicConfig.has_section("Keyboard 1"):
            sonicConfig.add_section("Keyboard 1")

        for x in sonicKeys:
            sonicConfig.set("Keyboard 1", f"{x}", f"{sonicKeys[x]}")

        # [Controller 1]
        if not sonicConfig.has_section("Controller 1"):
            sonicConfig.add_section("Controller 1")

        for index in playersControllers:
            controller = playersControllers[index]
            if controller.player_number != 1:
                continue
            for x in sonicButtons:
                sonicConfig.set("Controller 1", f"{x}", f"{sonicButtons[x]}")
            break

        with iniFile.open('w') as configfile:
            sonicConfig.write(configfile, False)

        os.chdir(rom)
        commandArray = [emu]

        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': generate_sdl_game_controller_config(playersControllers)
            })

    def getMouseMode(self, config, rom):
        rom_path = Path(rom)

        # Determine the emulator to use
        if rom_path.name.lower().endswith("son"):
            emu = "sonic2013"
        else:
            emu = "soniccd"

        mouseRoms = [
            "1bd5ad366df1765c98d20b53c092a528", # iOS version of SonicCD
        ]

        enableMouse = False
        data_file = rom_path / 'Data.rsdk'
        if emu == "soniccd" and data_file.is_file():
            enableMouse = self.__getMD5(data_file) in mouseRoms
        else:
            enableMouse = False

        return enableMouse

    def __getMD5(self, filename: Path) -> str:
        rp = filename.resolve()

        try:
            self.__getMD5.__func__.md5
        except AttributeError:
            self.__getMD5.__func__.md5 = dict()

        try:
            return self.__getMD5.__func__.md5[str(rp)]
        except KeyError:
            self.__getMD5.__func__.md5[str(rp)] = hashlib.md5(rp.read_bytes()).hexdigest()
            return self.__getMD5.__func__.md5[str(rp)]
