from __future__ import annotations

import codecs
from typing import TYPE_CHECKING

from ... import Command
from ...batoceraPaths import CONFIGS, SAVES, mkdir_if_not_exists
from ...controller import Controller
from ..Generator import Generator

if TYPE_CHECKING:
    from pathlib import Path

    from ...controller import Controllers
    from ...types import HotkeysContext


class EasyRPGGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "easyrpg",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"], "menu": "KEY_F9", "pause": "KEY_ESC", "restore_state": "KEY_F12", "save_state": "KEY_F11", "rewind": "KEY_F" }
        }

    def generate(self, system, rom, playersControllers, metadata, esmetadata, guns, wheels, gameResolution):
        commandArray: list[str | Path] = ["easyrpg-player"]

        # FPS
        if system.config.show_fps:
            commandArray.append("--show-fps")

        # Test Play (Debug Mode)
        if system.config.get_bool('testplay'):
            commandArray.append("--test-play")

        # Game Region (Encoding)
        encoding = system.config.get('encoding', 'auto')
        commandArray.extend(["--encoding", encoding if encoding != 'autodetect' else 'auto'])

        # Save directory
        savePath = SAVES / "easyrpg" / rom.name
        mkdir_if_not_exists(savePath)
        commandArray.extend(["--save-path", savePath])

        # Dir for logs and conf
        configdir = CONFIGS / "easyrpg"
        mkdir_if_not_exists(configdir)

        commandArray.extend(["--project-path", rom])

        EasyRPGGenerator.padConfig(configdir, playersControllers)

        return Command.Command(array=commandArray)

    @staticmethod
    def padConfig(configdir: Path, playersControllers: Controllers) -> None:
        keymapping: dict[str, str | None] = {
            "button_up": None,
            "button_down": None,
            "button_left": None,
            "button_right": None,
            "button_action": "a",
            "button_cancel": "b",
            "button_shift": "pageup",
            "button_n0": None,
            "button_n1": None,
            "button_n2": None,
            "button_n3": None,
            "button_n4": None,
            "button_n5": None,
            "button_n6": None,
            "button_n7": None,
            "button_n8": None,
            "button_n9": None,
            "button_plus": None,
            "button_minus": None,
            "button_multiply": None,
            "button_divide": None,
            "button_period": None,
            "button_debug_menu": None,
            "button_debug_through": None
        }

        with codecs.open(str(configdir / "config.ini"), "w", encoding="ascii") as f:
            f.write("[Joypad]\n")
            if pad := Controller.find_player_number(playersControllers, 1):
                f.write(f"number={pad.index}\n" )
                for key, value in keymapping.items():
                    button = -1
                    if value is not None and pad.inputs[value].type == "button":
                        button = pad.inputs[value].id
                    f.write(f"{key}={button}\n")
