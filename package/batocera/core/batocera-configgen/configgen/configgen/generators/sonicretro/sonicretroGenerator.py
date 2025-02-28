from __future__ import annotations

import hashlib
import os
from functools import cache
from pathlib import Path
from typing import TYPE_CHECKING

from ... import Command
from ...controller import Controller, generate_sdl_game_controller_config
from ...utils.configparser import CaseSensitiveRawConfigParser
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext


@cache
def _get_resolved_path_md5(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


# @cache is not used on this function because the digest should be cached by
# resolved path and we don't want the caller to have to remember to call .resolve()
def _get_path_md5(path: Path) -> str:
    return _get_resolved_path_md5(path.resolve())


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
        sonicConfig.set("Dev", "DevMenu", system.config.get_bool('devmenu', return_values=("true", "false")))
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
        sonicConfig.set("Dev", "UseHQModes", system.config.get_bool('hqmode', True, return_values=("true", "false")))
        sonicConfig.set("Dev", "DataFile", "Data.rsdk")

        # [Game]
        if not sonicConfig.has_section("Game"):
            sonicConfig.add_section("Game")

        if (emu == "sonic2013"):
            sonicConfig.set("Game", "SkipStartMenu", system.config.get_bool('skipstart', return_values=("true", "false")))
        else:
            sonicConfig.set("Game", "OriginalControls", system.config.get("spindash", "-1"))
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
        if game_config_bin.is_file() and _get_path_md5(game_config_bin) in originsGameConfig:
            sonicConfig.set("Game", "GameType", "1")

        sonicConfig.set("Game", "Language", system.config.get("language", "0"))

        # [Window]
        if not sonicConfig.has_section("Window"):
            sonicConfig.add_section("Window")

        sonicConfig.set("Window", "FullScreen", "true")
        sonicConfig.set("Window", "Borderless", "true")
        sonicConfig.set("Window", "VSync", system.config.get_bool("vsync", True, return_values=("true", "false")))
        sonicConfig.set("Window", "ScalingMode", system.config.get("scalingmode", "2"))
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

        for x, key in sonicKeys.items():
            sonicConfig.set("Keyboard 1", f"{x}", f"{key}")

        # [Controller 1]
        if not sonicConfig.has_section("Controller 1"):
            sonicConfig.add_section("Controller 1")

        if Controller.find_player_number(playersControllers, 1):
            for x, button in sonicButtons.items():
                sonicConfig.set("Controller 1", f"{x}", f"{button}")

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

        mouseRoms = [
            "1bd5ad366df1765c98d20b53c092a528", # iOS version of SonicCD
        ]

        data_file = rom_path / 'Data.rsdk'
        if not rom_path.name.lower().endswith("son") and data_file.is_file():
            return _get_path_md5(data_file) in mouseRoms

        return False
