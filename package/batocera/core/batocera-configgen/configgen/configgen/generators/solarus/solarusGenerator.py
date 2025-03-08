from __future__ import annotations

import codecs
from typing import TYPE_CHECKING, Final

from ... import Command
from ...batoceraPaths import CONFIGS, mkdir_if_not_exists
from ...controller import Controller, generate_sdl_game_controller_config
from ..Generator import Generator

if TYPE_CHECKING:
    from pathlib import Path

    from ...controller import Controllers
    from ...Emulator import Emulator
    from ...input import Input
    from ...types import HotkeysContext


_CONFIG_DIR: Final = CONFIGS / "solarus"

class SolarusGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "solarus",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"] }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        # basis
        commandArray: list[str | Path] = ["solarus-run", "-fullscreen=yes", "-cursor-visible=no", "-lua-console=no"]

        # hotkey to exit
        for nplayer, pad in enumerate(playersControllers, start=1):
            if nplayer == 1 and "hotkey" in pad.inputs and "start" in pad.inputs:
                commandArray.append(f"-quit-combo={pad.inputs['hotkey'].id}+{pad.inputs['start'].id}")
            commandArray.append(f"-joypad-num{nplayer}={pad.index}")

        # player pad
        SolarusGenerator.padConfig(system, playersControllers)

        # rom
        commandArray.append(rom)

        return Command.Command(array=commandArray, env={
            'SDL_VIDEO_MINIMIZE_ON_FOCUS_LOSS': '0' ,
            "SDL_GAMECONTROLLERCONFIG": generate_sdl_game_controller_config(playersControllers),
            "SDL_JOYSTICK_HIDAPI": "0"
        })

    @staticmethod
    def padConfig(system: Emulator, playersControllers: Controllers):
        keymapping = {
            "action": "a",
            "attack": "b",
            "item1":  "y",
            "item2":  "x",
            "pause":  "start",
            "right":  "right",
            "up":     "up",
            "left":   "left",
            "down":   "down"
        }

        reverseAxis = {
            "up": "down",
            "left": "right"
        }

        match system.config.get('joystick'):
            case "joystick1" | "joystick2" as joystick:
                keymapping["up"]    = f"{joystick}up"
                keymapping["down"]  = f"{joystick}down"
                keymapping["left"]  = f"{joystick}left"
                keymapping["right"] = f"{joystick}right"

        mkdir_if_not_exists(_CONFIG_DIR)
        with codecs.open(str(_CONFIG_DIR / "pads.ini"), "w", encoding="ascii") as f:
            if pad := Controller.find_player_number(playersControllers, 1):
                for key in keymapping:
                    if keymapping[key] in pad.inputs:
                        f.write(f"{key}={SolarusGenerator.key2val(pad.inputs[keymapping[key]], False)}\n")
                    if key in reverseAxis and pad.inputs[keymapping[key]].type == "axis":
                        f.write(f"{reverseAxis[key]}={SolarusGenerator.key2val(pad.inputs[keymapping[key]], True)}\n")

    @staticmethod
    def key2val(input: Input, reverse: bool):
        if input.type == "button":
            return f"button {input.id}"
        if input.type == "hat":
            if input.value == "1":
                return "hat 0 up"
            if input.value == "2":
                return "hat 0 right"
            if input.value == "4":
                return "hat 0 down"
            if input.value == "8":
                return "hat 0 left"
        if input.type == "axis":
            if (reverse and input.value == "-1") or (not reverse and input.value == "1"):
                return f"axis {input.id} +"
            return f"axis {input.id} -"
        return None
