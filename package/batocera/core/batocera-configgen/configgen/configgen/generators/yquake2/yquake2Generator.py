#
# This file is part of the batocera distribution (https://batocera.org).
# Copyright (c) 2025+.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# YOU MUST KEEP THIS HEADER AS IT IS
#
from __future__ import annotations

from typing import TYPE_CHECKING
from pathlib import Path

from ... import Command
from ...batoceraPaths import CONFIGS
from ...controller import Controller, generate_sdl_game_controller_config
from ...utils import esSettings, currentPlatform
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext

defaultConfig = Path( CONFIGS / "yquake2/baseq2/yq2.cfg" )

def createDefault():
    Path(CONFIGS / "yquake2/baseq2").mkdir(parents=True, exist_ok=True)

    # Define the default options to add
    options_to_set = {
        # Special keys for hotkey shortcuts
        "bind PRINT": "screenshot jpg 90",
        "bind MENU": "menu_joy",
        # Default gamepad controls
        "bind SHOULDR_LEFT": "+movedown",
        "bind TRIG_LEFT": "+moveup",
        "bind SHOULDR_RIGHT": "+joyaltselector",
        "bind TRIG_RIGHT": "+attack",
        "bind BTN_SOUTH": "+moveup",
        "bind BTN_EAST": "+movedown",
        "bind BTN_WEST": "weapnext",
        "bind BTN_NORTH": "weapprev",
        "bind BTN_BACK": "cmd help",
        "bind BTN_GUIDE": "",
        "bind STICK_LEFT": "",
        "bind STICK_RIGHT": "centerview",
        "bind DP_UP": "cycleweap weapon_plasmabeam weapon_boomer weapon_chaingun weapon_etf_rifle weapon_machinegun weapon_blaster",
        "bind DP_DOWN": "cycleweap weapon_supershotgun weapon_shotgun weapon_chainfist",
        "bind DP_LEFT": "cycleweap weapon_phalanx weapon_rocketlauncher weapon_proxlauncher weapon_grenadelauncher ammo_grenades",
        "bind DP_RIGHT": "cycleweap weapon_bfg weapon_disintegrator weapon_railgun weapon_hyperblaster ammo_tesla ammo_trap",
        "bind BTN_WEST_ALT": "invuse",
        "bind BTN_NORTH_ALT": "invdrop",
        "bind BTN_BACK_ALT": "inven",
        "bind DP_UP_ALT": "invprev",
        "bind DP_DOWN_ALT": "invnext",
        "bind DP_LEFT_ALT": "invprev",
        "bind DP_RIGHT_ALT": "invnext",
        # Gameplay options, check YQ2 documentation
        "set aimfix": "1",
        "set cl_run": "1",
        "set g_machinegun_norecoil": "1",
        "set g_quick_weap": "1",
        "set g_swap_speed": "2",
        # Audio & Video
        "set ogg_ignoretrack0": "1",
        "set gl_znear": "3.2",
        "set vid_fullscreen": "1",
        "set r_mode": "-2"
    }

    # Disable OpenAL on slow CPUs
    if currentPlatform.getCPUSpeed() < 2000:
        options_to_set["set s_openal"] = "0"

    if not currentPlatform.isPC():
        options_to_set["set gl1_discardfb"] = "1"
        options_to_set["set gl1_lightmapcopies"] = "1"
        options_to_set["set gl1_pointparameters"] = "0"

    with defaultConfig.open('w') as config_file:
        for key, value in options_to_set.items():
            config_file.write(f"{key} \"{value}\"\n")


class YQuake2Generator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "yquake2",
            "keys": {
                "exit": ["KEY_LEFTALT", "KEY_F4"],
                "save_state": "KEY_F6",
                "restore_state": "KEY_F9"
            }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        if not defaultConfig.exists():
            createDefault()

        romName = rom.name
        swapButtons = "1" if esSettings.getInvertButtonsValue() else "0"

        commandArray = [ "/usr/bin/yquake2/quake2", "-cfgdir", "configs/yquake2",
                         "+set", "joy_confirm", swapButtons ]

        if pad := Controller.find_player_number(playersControllers, 1):
            commandArray.extend([ "+set", "in_initjoy", str(pad.index + 1) ])

        # Mission Packs
        if "reckoning" in romName.lower():
            commandArray.extend(["+set", "game", "xatrix"])
        elif "zero" in romName.lower():
            commandArray.extend(["+set", "game", "rogue"])
        elif "zaero" in romName.lower():
            commandArray.extend(["+set", "game", "zaero"])

        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': generate_sdl_game_controller_config(playersControllers),
                'SDL_JOYSTICK_HIDAPI': '0'
            }
        )

    def getInGameRatio(self, config, gameResolution, rom):
        if gameResolution["width"] / float(gameResolution["height"]) > ((16.0 / 9.0) - 0.1):
            return 16/9
        return 4/3
