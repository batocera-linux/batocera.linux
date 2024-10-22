from __future__ import annotations

import codecs
from typing import TYPE_CHECKING, Final

from ... import Command
from ...batoceraPaths import CONFIGS, mkdir_if_not_exists
from ...controller import generate_sdl_game_controller_config
from ..Generator import Generator

if TYPE_CHECKING:
    from ...controller import ControllerMapping
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
        commandArray = ["solarus-run", "-fullscreen=yes", "-cursor-visible=no", "-lua-console=no"]

        # hotkey to exit
        nplayer = 1
        for playercontroller, pad in sorted(playersControllers.items()):
            if nplayer == 1:
                if "hotkey" in pad.inputs and "start" in pad.inputs:
                    commandArray.append("-quit-combo={}+{}".format(pad.inputs["hotkey"].id, pad.inputs["start"].id))
            commandArray.append(f"-joypad-num{nplayer}={pad.index}")
            nplayer += 1

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
    def padConfig(system: Emulator, playersControllers: ControllerMapping):
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

        if system.isOptSet('joystick'):
            if system.config['joystick'] == "joystick1":
                keymapping["up"]    = "joystick1up"
                keymapping["down"]  = "joystick1down"
                keymapping["left"]  = "joystick1left"
                keymapping["right"] = "joystick1right"
            elif system.config['joystick'] == "joystick2":
                keymapping["up"]    = "joystick2up"
                keymapping["down"]  = "joystick2down"
                keymapping["left"]  = "joystick2left"
                keymapping["right"] = "joystick2right"

        mkdir_if_not_exists(_CONFIG_DIR)
        f = codecs.open(str(_CONFIG_DIR / "pads.ini"), "w", encoding="ascii")

        nplayer = 1
        for playercontroller, pad in sorted(playersControllers.items()):
            if nplayer == 1:
                for key in keymapping:
                    if keymapping[key] in pad.inputs:
                        f.write(f"{key}={SolarusGenerator.key2val(pad.inputs[keymapping[key]], False)}\n")
                    if key in reverseAxis and pad.inputs[keymapping[key]].type == "axis":
                        f.write(f"{reverseAxis[key]}={SolarusGenerator.key2val(pad.inputs[keymapping[key]], True)}\n")

            nplayer += 1

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
                return f"axis {str(input.id)} +"
            else:
                return f"axis {str(input.id)} -"
        return None
