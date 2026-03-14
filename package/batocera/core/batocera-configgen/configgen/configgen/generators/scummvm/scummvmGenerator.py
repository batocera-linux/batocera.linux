from __future__ import annotations

import os
import re
from typing import TYPE_CHECKING, Final

from ... import Command
from ...batoceraPaths import BIOS, CACHE, CONFIGS, SAVES, SCREENSHOTS, ensure_parents_and_open, mkdir_if_not_exists
from ...controller import Controller, generate_sdl_game_controller_config
from ...utils.configparser import CaseSensitiveConfigParser
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext

scummConfigDir: Final = CONFIGS / "scummvm"
scummConfigFile: Final = scummConfigDir / "scummvm.ini"
scummExtra: Final = BIOS / "scummvm" / "extra"
scummSave: Final = SAVES / "scummvm"

class ScummVMGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "scummvm",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"], "menu": ["KEY_LEFTCTRL", "KEY_F5"] }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        # create /userdata/bios/scummvm/extra folder if it doesn't exist
        mkdir_if_not_exists(scummExtra)

        # create / modify scummvm config file as needed
        scummConfig = CaseSensitiveConfigParser()
        if scummConfigFile.exists():
            scummConfig.read(scummConfigFile)

        if not scummConfig.has_section("scummvm"):
            scummConfig.add_section("scummvm")
        # set gui_browser_native to false
        scummConfig.set("scummvm", "gui_browser_native", "false")

        # save the ini file
        with ensure_parents_and_open(scummConfigFile, 'w') as configfile:
            scummConfig.write(configfile)

        # Find rom path
        # 1. If a .scummvm file exists and contains a valid <game id>, use the <game id>
        # 2. If an empty <game id>.scummvm file exists, use the <game id>
        # 3. Otherwise, auto detect the game

        if rom.is_dir():
            # squashfs: find a <game name>.scummvm file
            rom_file = next(rom.glob("*.scummvm"), None)
            rom_path = rom
        else:
            # .scummvm: use rom as file
            rom_file = rom
            rom_path = rom.parent

        target = "--auto-detect"

        if rom_file is not None:
            game_id = rom_file.read_text().strip().lower() or rom_file.stem

            if re.match(r'^(?:[a-z0-9-]+:)?[a-z0-9-]+$', game_id) is not None:
                target = game_id

        # pad number
        id = 0
        if pad := Controller.find_player_number(playersControllers, 1):
            id = pad.index

        commandArray = ["/usr/bin/scummvm", "-f"]

        # set the resolution
        commandArray.append(f"--window-size={gameResolution['width']},{gameResolution['height']}")

        ## user options

        # scale factor
        commandArray.append(f"--scale-factor={system.config.get('scumm_scale', '3')}")

        # sclaer mode
        commandArray.append(f"--scaler={system.config.get('scumm_scaler_mode', 'normal')}")

        #  stretch mode
        if stretch := system.config.get("scumm_stretch"):
            commandArray.append(f"--stretch-mode={stretch}")

        # renderer
        commandArray.append(f"--renderer={system.config.get('scumm_renderer', 'opengl')}")

        # language
        if language := system.config.get("scumm_language"):
            commandArray.extend(["-q", f"{language}"])

        # logging
        commandArray.append("--logfile=/userdata/system/logs/scummvm.log")

        commandArray.extend(
            [f"--joystick={id}",
            f"--screenshotspath={SCREENSHOTS}",
            f"--extrapath={scummExtra}",
            f"--savepath={scummSave}",
            f"--path={rom_path}",
            f"{target}"]
        )

        # Determine SDL Video Driver
        sdl_videodriver = "wayland" if "WAYLAND_DISPLAY" in os.environ else "x11"

        return Command.Command(
            array=commandArray,
            env={
                "SDL_VIDEODRIVER": sdl_videodriver,
                "XDG_CONFIG_HOME": CONFIGS,
                "XDG_CACHE_HOME": CACHE,
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_game_controller_config(playersControllers)
            }
        )

    def getInGameRatio(self, config, gameResolution, rom):
        if config.get("scumm_stretch") in ["fit_force_aspect", "pixel-perfect"]:
            return 4/3
        return 16/9
