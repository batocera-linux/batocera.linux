from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING

from ... import Command
from ...batoceraPaths import ensure_parents_and_open
from ...controller import generate_sdl_game_controller_config
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext

eslog = logging.getLogger(__name__)

Keymapping =[
        {
			"Joystick": -1,
			"Buttons": [
				"UP",
				"DOWN",
				"LEFT",
				"RIGHT",
				"a",
				"s",
				"d",
				"z",
				"x",
				"c",
				"RETURN",
				"f",
				"v",
				"q"
			]
		},
		{
			"Joystick": -1,
			"Buttons": [
				"KP_8",
				"KP_5",
				"KP_4",
				"KP_6",
				"p",
				"LBRACKET",
				"RBRACKET",
				"SEMICOLON",
				"QUOTE",
				"BACKSLASH",
				"SLASH",
				"o",
				"l",
				"PERIOD"
			]
		},
		{
			"Joystick": -1,
			"Buttons": [
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used"
			]
		},
		{
			"Joystick": -1,
			"Buttons": [
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used"
			]
		}
	]

Joymapping =[
        {
			"Joystick": 0,
			"Buttons": [
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used"
			]
		},
        {
			"Joystick": 1,
			"Buttons": [
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used"
			]
		},
		{
			"Joystick": 2,
			"Buttons": [
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used"
			]
		},
		{
			"Joystick": 3,
			"Buttons": [
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used",
				"Not used"
			]
		}
	]

class IkemenGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "ikemen",
            "keys": { "exit": "KEY_Q", "menu": "KEY_ESC", "pause": "KEY_ESC" }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        rom_path = Path(rom)
        config_path = rom_path / "save" / "config.json"

        try:
            with config_path.open() as c:
                conf = json.load(c)
        except:
            conf = {}

        # Joystick configuration seems completely broken in 0.98.2 Linux
        # so let's force keyboad and use a pad2key
        conf["KeyConfig"] = Keymapping
        conf["JoystickConfig"] = Joymapping
        conf["Fullscreen"] = True

        js_out = json.dumps(conf, indent=2)
        with ensure_parents_and_open(config_path, "w") as jout:
            jout.write(js_out)

        commandArray = ["/usr/bin/batocera-ikemen", rom]

        return Command.Command(array=commandArray, env={ "SDL_GAMECONTROLLERCONFIG": generate_sdl_game_controller_config(playersControllers) })
